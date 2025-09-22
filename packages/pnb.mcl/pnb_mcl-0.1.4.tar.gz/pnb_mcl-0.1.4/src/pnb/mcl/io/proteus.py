import json
import subprocess

from pnb.mcl.metamodel import standard as metamodel

from pnb.mcl.io.xmi import read_xmi

CALL_TOOLBOX = [r'E:\s\py_s312\Scripts\python.exe', '-OO', r'E:\s\w\p\skas\src\python\dexpilib\dexpilib\pnb_pid_proteus_python.py']
#CALL_TOOLBOX = [r'E:\s\w\p\skas\src\python\pnbuild\examples\pnb_toolbox_library\.build_py2exe\pnb_pid_proteus_python.exe']
# CALL_TOOLBOX = [r'E:\s\py_s312\Scripts\python.exe', '-OO', '-m', 'cProfile', '-o', 'dstats', '-m', 'dexpilib.pnb_pid_proteus_python', ]
DEXPI_1_4_XMI = r'E:\s\w\p\pnb.mcl\public_demo\DEXPI P&ID Specification 1.4 fixed.xmi'

FS = b'\x1c'




from skas import run





class ProteusReader:

    def __init__(self, source):
        

        if 1:
        
            source = str(source)
    
            
            json_task = {
                "module":"dexpilib.api",
                "task":"proteus2json",
                "params":{
                    "proteus_path":source,
                    "source_dexpi_version":"auto",
                    "target_dexpi_version":"pnb::pid::dexpi_1_4"}}
            
            popen = subprocess.Popen(CALL_TOOLBOX, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
            popen.stdin.write(json.dumps(json_task).encode('utf-8'))
            popen.stdin.write(FS)
            popen.stdin.flush()
            
            result_parts = []
    
            # also check if popen.stdout "is true"?
            while True:
                part = popen.stdout.read()
    
                if FS in part:
                    assert part.count(FS) == 1
                    pre, post = part.split(FS)
                    result_parts.append(pre)
                    break
    
                result_parts.append(part)
                if popen.returncode is not None:
                    break
                
                
    
            #print(time.time() -t)
            #import sys
            #sys.exit()
            
            
                
            result_string = b''.join(result_parts).strip()
            json_result = json.loads(result_string)

            result = json_result.get('result')
            parsed = json.loads(result)

            
        else:
            
            
            
            
            
            json_result = run.run_proteus_to_json_dict(str(source), 'pnb::pid::dexpi_1_4', 'pnb::pid::dexpi_1_4', skip_import_data=True)
            parsed = json_result#.get('result')
       

        
        self.errors = json_result.get('errors', '')
        self.infos = json_result.get('infos', '')
        
        print(self.errors, self.infos)
        
        
        
        
        self.information_model = read_xmi(DEXPI_1_4_XMI)
        
        self.type_by_name = {}
        for p in self.information_model.packagedElements:
            for sp in p.packagedElements:
                if isinstance(sp, metamodel.Type):
                    assert sp.name not in self.type_by_name
                    self.type_by_name[sp.name] = sp
                    
        self.object_by_id = {}
        self.reference_prop_data = []
       
        
        self.pid_model = metamodel.Model('pid', uri='http:www.pid.org')
        
        documents = parsed.get('documents', [])
        if not documents:
            self.model = None
        else:
            assert len(documents) == 1
            self.model = self._json_to_model(documents[0])
            self.pid_model.add(self.model)
            
        for owner, prop, values_data in self.reference_prop_data:
            values = []
            for value_data in values_data:
                assert value_data['#type'] == 'pnb::json::ObjectRef'
                idref = value_data['#idref']
                value = self.object_by_id[idref]
                values.append(value)
            prop._set_values_(owner, values)
  
            
    def _json_to_model(self, model_dict):
        
        return self._json_to_python(model_dict)
    
    
    def _json_to_python(self, value_dict):
        
        
        type_name = value_dict.pop('#type')
        
        prefix = 'pnb::pid::dexpi_1_4::'
        assert type_name.startswith(prefix), type_name
        type_name = type_name[len(prefix):]
        
        type_ = self.type_by_name.get(type_name)
        
        
        if isinstance(type_, metamodel.ConcreteClass):
            value = type_()
            id_ = value_dict.pop('#id')
            self.object_by_id[id_] = value
            
            for prop_name, prop_value_dicts in value_dict.items():
                
                # cf. xmi fix_name
                prop_name = prop_name.replace('/', '_PER_')
                prop_name = prop_name.replace(',', '_COMMA_')
                prop_name = prop_name.replace('(', '_')
                prop_name = prop_name.replace(')', '_')

                prop = type_.attributes[prop_name]
                if isinstance(prop, metamodel.ReferenceProperty):
                    self.reference_prop_data.append((value, prop, prop_value_dicts))
                else:
                    values = [self._json_to_python(prop_value_dict) for prop_value_dict in prop_value_dicts]
                    prop._set_values_(value, values)
                    
        elif isinstance(type_, metamodel.AggregatedDataType):
            value = type_()
            for prop_name, prop_value_dicts in value_dict.items():
                prop = type_.attributes.get(prop_name)
                assert isinstance(prop, metamodel.DataProperty)
                values = [self._json_to_python(prop_value_dict) for prop_value_dict in prop_value_dicts]
                prop._set_values_(value, values)
           
        elif isinstance(type_, metamodel.BooleanType):
            value = value_dict['value']
            assert isinstance(value, bool)
        elif isinstance(type_, metamodel.DoubleType):
            value = float(value_dict['value']) 
        elif isinstance(type_, metamodel.IntegerType):
            value = int(value_dict['value'])
        elif isinstance(type_, metamodel.StringType):
            value = value_dict['value']
        elif isinstance(type_, metamodel.Enumeration):
            value = type_.ownedLiterals.at(value_dict['value'])
        elif isinstance(type_, metamodel.SingletonType):
            value = type_.value
        else:
            raise Exception(type_name, type_)

        return value

        
        

