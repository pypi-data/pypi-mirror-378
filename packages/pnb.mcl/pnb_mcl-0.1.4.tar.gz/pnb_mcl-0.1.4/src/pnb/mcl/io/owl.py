import itertools
import sys

import rdflib
from rdflib import Literal, RDF, BNode, OWL, RDFS, XSD


class OwlExporter:

    def __init__(self, model, prefix=None, uri=None):
        
        self.redundantSubClassAxioms = True
        self.redundantTypeAxioms = True
        self.abstractSuperProperties = True
        self.topLevelTypes = True
        
        self.model = model
        self.namespace = rdflib.Namespace(uri or (model.uri + '#'))
        self.metamodel = sys.modules[model.__module__]
        self.graph = rdflib.Graph()
        self.graph.bind(prefix or self.model.name, self.namespace)
        self.node_by_element = {}
        self.element_by_node = {}
        self.defined_nodes = set()
        
        self.graph.add((rdflib.URIRef(str(self.namespace)[:-1]), RDF.type, OWL.Ontology))
        
        self.value_property = self.namespace.value
        self.graph += [
            (self.value_property, RDF.type, OWL.DatatypeProperty),
            (self.value_property, RDF.type, OWL.FunctionalProperty)]

        if self.abstractSuperProperties:
            
            self.composition_property = self.namespace.CompositionProperty
            self.graph += [
                (self.composition_property, RDF.type, OWL.ObjectProperty)]
            
            self.reference_property = self.namespace.ReferenceProperty
            self.graph += [
                (self.reference_property, RDF.type, OWL.ObjectProperty)]
            
            self.data_property = self.namespace.DataProperty
            self.graph += [
                (self.data_property, RDF.type, OWL.ObjectProperty)]

        self.add_element(model)

        undefined_nodes = set(self.element_by_node).difference(self.defined_nodes)
        assert not undefined_nodes, undefined_nodes
        
        top_level_classes = [
            element for element in self.node_by_element
            if isinstance(element, self.metamodel.Class) and not element.superTypes]
        
        self._add_disjointness_if_applicable(top_level_classes, 'top_level_classes')

        top_level_datatypes = [
            element for element in self.node_by_element
            if isinstance(element, self.metamodel.DataType) and not element.superTypes]
        
        self._add_disjointness_if_applicable(top_level_datatypes, 'top_level_datatypes')
        
        if self.topLevelTypes:
            
            self.graph += [
                (self.namespace.Object, RDF.type, OWL.Class)]
            self.graph += equivalent_union(self.namespace.Object, [self.get_node(c) for c in top_level_classes])
            
            if self.redundantSubClassAxioms:
                for c in top_level_classes:
                    self.graph.add((self.get_node(c), RDFS.subClassOf, self.namespace.Object))  

            self.graph += [
                (self.namespace.DataValue, RDF.type, OWL.Class)]
            self.graph += equivalent_union(self.namespace.DataValue, [self.get_node(c) for c in top_level_datatypes])
            
            if self.redundantSubClassAxioms:
                for c in top_level_datatypes:
                    self.graph.add((self.get_node(c), RDFS.subClassOf, self.namespace.DataValue))
    
            self.graph += all_disjoint_classes((self.namespace.Object,  self.namespace.DataValue))
            
            
            if self.abstractSuperProperties:
                self.graph += [
                    (self.composition_property, RDFS.domain, self.namespace.Object),
                    (self.composition_property, RDFS.range, self.namespace.Object)]
                
                self.graph += [
                    (self.reference_property, RDFS.domain, self.namespace.Object),
                    (self.reference_property, RDFS.range, self.namespace.Object)]
                
                
                object_or_data_value = union_of((self.namespace.Object, self.namespace.DataValue))
                self.graph += object_or_data_value
                
                self.graph += [
                    (self.data_property, RDFS.domain, object_or_data_value.class_),
                    (self.data_property, RDFS.range, self.namespace.DataValue)]
                    

                
                
                
                


    def get_node(self, element):
        node = self.node_by_element.get(element)
        if node is None:
            if isinstance(element, (self.metamodel.Type, self.metamodel.SingletonValue)):
                name = element.name
            elif isinstance(element, (self.metamodel.EnumerationLiteral, self.metamodel.Property)):
                name = element.owner.name + '.' + element.name
            else:
                raise Exception(element)
            node = self.namespace.term(name)
            self.node_by_element[element] = node
            assert node not in self.element_by_node
            self.element_by_node[node] = element
        return node

    def def_node(self, element, owl_type):
        node = self.get_node(element)
        assert node not in self.defined_nodes
        self.graph.add((node, RDF.type, owl_type))
        self.defined_nodes.add(node)
        return node

    def add_element(self, element):
        if isinstance(element, self.metamodel.Model):
            for pe in element.packagedElements:
                self.add_element(pe)
                # TODO: unnamed objects
        elif isinstance(element, self.metamodel.Package):
            for pe in element.packagedElements:
                self.add_element(pe)
        elif isinstance(element, self.metamodel.Type):
            self.add_type(element)
        else:
            pass
        
        
    def _add_disjointness_if_applicable(self, types, info):
        if len(types) < 2:
            return
        
        types = [type_ for type_ in types if type_.name not in ['ColumnSection', 
                                                                'Vent']]
                                                                
                                  
        if info == 'top_level_classes':      
                                                                
            types = [type_ for type_ in types if type_.name not in [
                                                                
                                                                'CustomAttributeOwner',
                                                                'CustomObject',
                                                                'ChamberOwner',
                                                                'NozzleOwner',
                                                                'PipingNodeOwner',
                                                                'TransmissionDriver',
                                                                'ActuatingElectricalLocation',
                                                                'SensingLocation',
                                                                'SignalConveyingFunctionSource',
                                                                'SignalConveyingFunctionTarget',
                                                                'PipingConnection',
                                                                'PipingSourceItem',
                                                                'PipingTargetItem',
                                                                'PipingNetworkSegmentItem',
                                                                'IndustrialComplexParentStructure',
                                                                'PlantAreaLocatedStructure',
                                                                'PlantSectionParentStructure',
                                                                'PlantSystemLocatedStructure',
                                                                'PlantTrainLocatedStructure',
                                                                'ProcessPlantParentStructure',
                                                                'TechnicalItemParentStructure',
                                                                ]]
        
        
        
        applicable = True
        common_subtypes = set()
        print('########################')
        for type_ in types:
            print('+++', type_)
            if type_ in common_subtypes:
                applicable = False
                break
            common_subtypes.add(type_)
            new_subtypes = type_.allSubTypes
            if not common_subtypes.isdisjoint(new_subtypes):
                applicable = False
                break
            common_subtypes.update(new_subtypes)
        if not applicable:
            print(common_subtypes.intersection(new_subtypes))
            print(f'### {info} {", ".join(sorted(t.name for t in types))} not disjoint')
            assert False
            return
        
        self.graph += all_disjoint_classes(self.get_node(type_) for type_ in types)


        
    def add_type(self, type_):

        node = self.def_node(type_, OWL.Class)
        subTypes = list(type_.subTypes)
        
        self._add_disjointness_if_applicable(subTypes, type_)
        
        subTypeNodes = [self.get_node(subType) for subType in subTypes]
        
        if self.redundantSubClassAxioms or not type_.isAbstract:
            for subTypeNode in subTypeNodes:
                self.graph.add((subTypeNode, RDFS.subClassOf, node))
        
        if type_.isAbstract:
            self.graph += equivalent_union(node, subTypeNodes)

        if isinstance(type_, self.metamodel.PrimitiveType):
            
            name = type_.name
            xsd_name = name[0].lower() + name[1:] 
            xsd_node = getattr(XSD, xsd_name)
            self.graph += restrict_all_values_from(node, self.value_property, OWL.DatatypeProperty, xsd_node)
            self.graph += restrict_min_cardinality(node, self.value_property, OWL.DatatypeProperty, 1)

            
        if isinstance(type_, self.metamodel.Enumeration):
            literal_nodes = [self.def_node(literal, OWL.NamedIndividual) for literal in type_.orderedOwnedLiterals]
            assert len(literal_nodes), type_
            if not literal_nodes:
                ERROR
            if self.redundantTypeAxioms:
                for literal_node in literal_nodes:
                    self.graph.add((literal_node, RDF.type, node))
            self.graph += equivalent_one_of(node, literal_nodes)
            if len(literal_nodes) > 1:
                self.graph += all_different(literal_nodes)
                
        if isinstance(type_, self.metamodel.SingletonType):
            value = type_.value
            assert value
            value_node = self.def_node(value, OWL.NamedIndividual)
            if self.redundantTypeAxioms:
                self.graph.add((value_node, RDF.type, node))
            self.graph += equivalent_one_of(node, [value_node])
            
            
            
            
            
            
            
        if type_.name == 'CustomAttribute':
            value_prop_node = self.namespace.term('CustomAttribute.Value')
            self.graph += [
                (value_prop_node, RDF.type, OWL.ObjectProperty),
                (value_prop_node, RDFS.domain, node)]

            self.graph += restrict_cardinality(node, value_prop_node, OWL.ObjectProperty, 1)

            if self.abstractSuperProperties:
                self.graph.add((value_prop_node, RDFS.subPropertyOf, self.data_property))
            
            
            
            
        for prop in type_.ownedAttributes:
            
            is_ca_value = False
            if prop.name == 'Value' and type_.name.startswith('Custom'):
                assert len(list(type_.superTypes)) == 1, prop
                if list(type_.superTypes)[0].name == 'CustomAttribute':
                    is_ca_value = True
                
                
                
            if not is_ca_value:
                
                           
            
            
                prop_node = self.def_node(prop, OWL.ObjectProperty)
                
                self.graph += [
                    (prop_node, RDFS.domain, node),
                    (prop_node, RDFS.range, self.get_node(prop.type))]
                
                if self.abstractSuperProperties:
                    super_prop_node = {
                        self.metamodel.CompositionProperty: self.composition_property,
                        self.metamodel.ReferenceProperty: self.reference_property,
                        self.metamodel.DataProperty: self.data_property}[type(prop)]
                    self.graph.add((prop_node, RDFS.subPropertyOf, super_prop_node))
                    
                if prop.lower == prop.upper:
                    self.graph += restrict_cardinality(node, prop_node, OWL.ObjectProperty, prop.lower, False)
                    
                else:
                    if prop.lower > 0:
                        self.graph += restrict_min_cardinality(node, prop_node, OWL.ObjectProperty, prop.lower, False)
                    if prop.upper is not None:
                        self.graph += restrict_max_cardinality(node, prop_node, OWL.ObjectProperty, prop.upper, False)
                    
            else:
                prop_node = self.namespace.term('CustomAttribute.Value')
                self.graph += restrict_all_values_from(node, prop_node, OWL.ObjectProperty, self.get_node(prop.type))
                

                
                
                

                    
      

            
            

          #  ji
            
            
                
                
                
                


    


                





"""
:todo Doc:
"""


__docformat__ = 'restructuredtext en'



import itertools
import operator

import six



import rdflib
from rdflib import OWL, RDF, RDFS, XSD

#import rdfutils
#from rdfutils import owlutils
#from attrs_utils import define



BASE = rdflib.Namespace('http://www.aixcape.org/oimel/base.owl#')



def paragraphs(text):
    
    
    pars = []
    par_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            par_lines.append(line)
        elif par_lines:
            pars.append(' '.join(par_lines))
            par_lines = []
    if par_lines:
        pars.append(' '.join(par_lines))
    return '\n'.join(pars)


class Uml2OwlConversion(object):
    """:todo Doc:"""

    def __init__(self):
        self.owl_graph = rdflib.ConjunctiveGraph()
        self.uri_by_element = {}
        self._element_by_uri = {}
        self.graph_by_package = {}
        self.infos_by_element = {}
        self.warnings_by_element = {}
        
        self.uml_subtypes_by_uml_type = {}
        
        self._all_uml_subtypes_by_uml_type = {}
        
        
    def arrange_types(self):
        
        all_subtypes = set()
        
        for element in self._element_by_uri.values():
            if isinstance(element, uml.Type):
                all_subtypes.update(self.get_all_uml_subtypes(element).difference((element, )))
                
        self.top_level_types = set(
            element for element in self._element_by_uri.values()
            if isinstance(element, uml.Type))
        self.top_level_types.difference_update(all_subtypes)

        
    def get_all_uml_subtypes(self, type_):
        
        result = self._all_uml_subtypes_by_uml_type.get(type_)
        if result is None:
            result = set((type_, ))
            for subtype in self.uml_subtypes_by_uml_type.get(type_, []):
                result.update(self.get_all_uml_subtypes(subtype))
            result = frozenset(result)
            self._all_uml_subtypes_by_uml_type[type_] = result
            
        return result
        
        


    def add_warning(self, element, message, formatter=paragraphs):
        """:todo Doc:"""
        self.warnings_by_element.setdefault(element, []).append(
            formatter(message))
  
    def add_info(self, element, message, formatter=paragraphs):
        assert isinstance(element, uml.Element)
        assert isinstance(message, six.text_type)
        self.infos_by_element.setdefault(element, []).append(
            formatter(message))

        
        
    def register_element(self, element, uri):
        """:todo Doc:"""
        
        assert isinstance(element, uml.Element)
        if element in self.uri_by_element:
            ERROR        
        if uri is not None:
            assert isinstance(uri, rdflib.URIRef)
            if not rdfutils.is_uriref(uri):
                ERROR
            if uri in self._element_by_uri:
                assert uri not in self._element_by_uri, uri
                ERROR

        self.uri_by_element[element] = uri
        if uri is not None:
            self._element_by_uri[uri] = element


    def get_element_uri(self, element, required=True):
        try:
            result = self.uri_by_element[element]
            if required and result is None:
                ERRIR
            return result
        except KeyError:
            if required:
                raise
            else:
                return None      
            

    def get_element_uris(self, elements):
        return [self.get_element_uri(element) for element in elements]
                  

    
# TODO begin final


class Uml2OwlConverterConfig:
    local_enumeration_literal_uris: bool=False
    merge_packages: bool=False
    
    

class Uml2OwlConverter(object):
    """:todo Doc:"""

    def __init__(self, config=Uml2OwlConverterConfig()):
        """:todo Doc:"""
        
        self.config = config

        self._owl_ext = '.owl'
        self._owl_sep = '#'
        self._owl_type_by_uml_primitive_type = {
            uml.Boolean: XSD.boolean,
            uml.String: XSD.string,
            uml.Integer: XSD.integer,
            uml.Real: XSD.decimal}


    def run(self, package, conversion=None):
        """:todo Doc:"""
        
        

        if not conversion:
            conversion = Uml2OwlConversion()


        
        self._convert_types(package, conversion)
        self._convert_generalizations(package, conversion)
        self._add_generalization_axioms(package, conversion)
        
        self._convert_enumeration_literals(package, conversion)
        self._convert_instances(package, conversion)
        
        self._complete_primitives(package, conversion)
        if 0:
        
            self._convert_enumerations(package, conversion)
            
            self._convert_primitive_types(package, conversion)
            self._convert_generalizations(package, conversion)
            self._convert_generalization_sets(package, conversion)
            
            
            
            
        self._convert_properties(package, conversion)
            
        
        

        return conversion
    
# TODO end final




    def _add_generalization_axioms(self, root_package, conversion):
        conversion.arrange_types()
        for supertype, subtypes in itertools.chain(
                conversion.uml_subtypes_by_uml_type.items(),
                [(None, conversion.top_level_types)]):

            subtype_uris = {
                conversion.get_element_uri(subtype)
                for subtype in subtypes}
            graph = self._get_graph_for_type(
                root_package, conversion, supertype)

            if supertype and supertype.uml_isAbstract:
                supertype_uri = conversion.get_element_uri(supertype)
                graph += owlutils.equivalent_union(supertype_uri, subtype_uris) 
            if len(subtypes) > 1:
                indirect_subtypes = set()
                for subtype in subtypes:
                    new_subtypes = conversion.get_all_uml_subtypes(subtype)
                    if not indirect_subtypes.isdisjoint(new_subtypes):
                        info = indirect_subtypes.intersection(new_subtypes)
                        info = ' from '+ subtype.uml_name + ': ' + ', '.join(cls.uml_name for cls in info) + ' from '+ subtype.uml_name 
                        print(f'subtypes of {supertype.uml_name if supertype else "TOP"} not disjoint: {info}')
                        break
                    indirect_subtypes.update(new_subtypes)
                else:
                    graph += owlutils.all_disjoint_classes(subtype_uris)



    
    


    
# TODO begin final




    def _convert_enumeration_literals_of_enumeration(
            self, root_package, conversion, enumeration):
        # pylint: disable=invalid-name
        """:todo Doc:"""

        if enumeration.uml_isAbstract:
            if enumeration.uml_ownedLiteral:
                conversion.add_warning(
                    enumeration,
                    '''The EnumerationLiterals of this Enumeration have been
                        skipped because the Enumeration is abstract.''')
            return

        if not enumeration.uml_ownedLiteral:
            conversion.add_warning(
                enumeration,
                '''For this non-abstract Enumeration, no EnumerationLiterals are
                    given.''')
            return

        enumeration_uri = conversion.get_element_uri(enumeration)
        literal_uris = []

        for literal in enumeration.uml_ownedLiteral:
            literal_uri = self._create_uri_for_enumeration_literal(
                root_package, conversion, literal)
            literal_uris.append(literal_uri)
            conversion.register_element(literal, literal_uri)
            literal_graph = self._get_graph_for_enumeration_literal(
                root_package, conversion, literal)
            literal_graph += owlutils.a_named_individual(
                literal_uri, enumeration_uri)

        enumeration_graph = self._get_graph_for_type(
            root_package, conversion, enumeration)
        enumeration_graph += owlutils.equivalent_one_of(
            enumeration_uri, literal_uris)
        if len(literal_uris) > 1:
            enumeration_graph += owlutils.all_different(literal_uris)


    def _create_uri_for_enumeration_literal(
            self, root_package, conversion, enumeration_literal):
        """:todo Doc:"""
        
        namespace = self._get_graph_for_enumeration_literal(
            root_package, conversion, enumeration_literal).identifier
            
        if self.config.local_enumeration_literal_uris:
            enumeration = enumeration_literal.uml_owner
            return self._create_uri(
                f'{enumeration.uml_name}.{enumeration_literal.uml_name}',
                namespace)
        else:
            return self._create_uri_from_name(
                root_package, conversion, enumeration_literal, namespace)

    def _get_graph_for_enumeration_literal(
            self, root_package, conversion, enumeration_literal):
        """:todo Doc:"""

        package = enumeration_literal.uml_enumeration.uml_package
        return self._get_graph_for_package(root_package, conversion, package)
    
    
    def _convert_instances(self, root_package, conversion):
        """:todo Doc:"""

        for nested_package in self._iter_nested_packages(root_package):
            for packaged_element in nested_package.uml_packagedElement:
                if type_is(packaged_element, uml.InstanceSpecification):
                    self._convert_instance(
                        root_package, conversion, packaged_element)
                    
                    
    def _convert_instance(self, root_package, conversion, instance):
        # pylint: disable=invalid-name
        """:todo Doc:"""

        package = instance.uml_owner
        namespace = self._get_graph_for_package(root_package, conversion, package).identifier
        uri = self._create_uri(instance.uml_name, namespace)
        conversion.register_element(instance, uri)
        graph = self._get_graph_for_package(root_package, conversion, package)
        graph += owlutils.a_named_individual(uri)

        classifiers = instance.uml_classifier
        assert len(classifiers) == 1

        classifier = set(classifiers).pop()
        classifier_uri = conversion.get_element_uri(classifier)

        graph += [(uri, RDF.type, classifier_uri)]
        graph += owlutils.equivalent_one_of(classifier_uri, [uri])

    def _convert_generalizations(self, root_package, conversion):
        """:todo Doc:"""

        for nested_package in self._iter_nested_packages(root_package):
            for packaged_element in nested_package.uml_packagedElement:
                if isinstance(packaged_element, uml.Type):
                    if not isinstance(packaged_element, uml.Association):
                        self._convert_generalizations_of_type(
                            root_package, conversion, packaged_element)
                        
                        
                        
                        
    def _complete_primitives(self, root_package, conversion):
        """:todo Doc:"""

        for nested_package in self._iter_nested_packages(root_package):
            for packaged_element in nested_package.uml_packagedElement:
                if type_is(packaged_element, uml.PrimitiveType):
                    primitive_type = packaged_element
                    
                    graph = self._get_graph_for_type(
                        root_package, conversion, primitive_type)
                    
                    value_uri = self._create_uri('value', graph.identifier)
                    
                    primitive_type_uri = conversion.get_element_uri(primitive_type)
                    
                    graph += [
                        (value_uri, RDF.type, OWL.DatatypeProperty),
                        (value_uri, RDF.type, OWL.FunctionalProperty)]
                    
                    
                    type_uri = dict(
                        AnyURI=XSD.anyURI,
                        Boolean=XSD.boolean,
                        DateTime=XSD.dateTime,
                        Double=XSD.double,
                        Integer=XSD.integer,
                        String=XSD.string,
                        UnsignedByte=XSD.unsignedByte)[primitive_type.uml_name]
                    
                    
                    graph += owlutils.restrict_all_values_from(
                        primitive_type_uri, value_uri, OWL.DatatypeProperty, type_uri)
                    graph += owlutils.restrict_min_cardinality(
                        primitive_type_uri, value_uri, OWL.DatatypeProperty, 1)
                        
                        
                        
                  
                    
                    
                    
                    
                    
                    
                    

                    
 
                        
                        
                        
                        
                        
                        
                        

    def _convert_generalizations_of_type(
            self, root_package, conversion, class_):
        """:todo Doc:"""

        class_uri = conversion.get_element_uri(class_)

        for generalization in class_.uml_generalization:
            general = generalization.uml_general
            general_uri = conversion.get_element_uri(
                general, required=False)
            if general_uri:
                graph = self._get_graph_for_generalization(
                    root_package, conversion, generalization)
                graph += owlutils.sub_class_of(class_uri, general_uri)
                conversion.register_element(generalization, None)
                conversion.uml_subtypes_by_uml_type.setdefault(
                    general, set()).add(class_)

    def _get_graph_for_generalization(
            self, root_package, conversion, generalization):
        """:todo Doc:"""

        return self._get_graph_for_package(
            root_package, conversion, generalization.uml_specific.uml_package)



# TODO end final

    def _convert_properties(self, root_package, conversion):
        """:todo Doc:"""

        properties, associations = (
            self._get_properties_and_associations_in_scope(
                root_package, conversion))

        for items, converter in [
                (properties, self._convert_non_assoc_property),
                (associations, self._convert_properties_of_association)]:
            items = apply_while_progress(
                items=items,
                function=lambda item, converter=converter: converter(
                    root_package, conversion, item, is_final_run=False))
            for item in items:
                handled = converter(
                    root_package, conversion, item, is_final_run=True)
                assert handled


    def _get_properties_and_associations_in_scope(
            self, root_package, conversion):
        """:todo Doc:"""

        associations = list(itertools.chain.from_iterable(
            (packaged_element
               for packaged_element in nested_package.uml_packagedElement
               if type_is(packaged_element, uml.Association))
            for nested_package in self._iter_nested_packages(root_package)))

        # This is for membership testing only, see below.
        associations_as_set = set(associations)
        assert len(associations) == len(associations_as_set)

        properties = []
        for nested_package in self._iter_nested_packages(root_package):
            for packaged_element in nested_package.uml_packagedElement:
                if isinstance(packaged_element, (uml.Class, uml.DataType)):
                    for owned_attribute in packaged_element.uml_ownedAttribute:
                        if type_is(owned_attribute, uml.Property):
                            if owned_attribute.uml_association:
                                if (owned_attribute.uml_association
                                        not in associations_as_set):
                                    WARN
                            else:
                                properties.append(owned_attribute)
                         #       print(owned_attribute.uml_name)
                                
        return properties, associations


    def _convert_non_assoc_property(
            self, root_package, conversion, property_, is_final_run):
        """:todo Doc:"""

        if property_.uml_redefinedProperty and property_.uml_subsettedProperty:
            TODO
            return True
        elif property_.uml_subsettedProperty:
            TODO
        elif property_.uml_redefinedProperty:
            
            return self._convert_non_assoc_property_redefining(
                root_package, conversion, property_, is_final_run)
        else:
            return self._convert_non_assoc_property_non_redefining(
                root_package, conversion, property_, is_final_run)


    def _convert_non_assoc_property_non_redefining(
            self, root_package, conversion, property_, is_final_run):
        """:todo Doc:"""

        type_uri, owl_property_type = (
            self._get_type_uri_and_owl_property_type_for_non_assoc_property(
                conversion, property_, {}))
        assert owl_property_type
       # if (type_uri, owl_property_type) == (None, None):
       #     return True
       # assert type_uri and owl_property_type

        # TODO: check/warn inconsistent redefinitions:
        # for each subclass of prop class (including indirect subclasses),
        # there must be exactly one unambiguous 'variant' of this property
        # (either a redefinition, or this property itself). 

        property_uri = self._create_uri_for_standalone_property(
            root_package, conversion, property_)
        conversion.register_element(property_, property_uri)

        upper = property_.uml_upper
        lower = property_.uml_lower

        if upper == lower == 0:
            ko
            conversion.add_warning(
                property_,
                'This Property (which is not a redefinition of another '
                  'Property) has an upper limit of 0. Thus, using the '
                  'corresponding OWL property will cause an inconsistent '
                  'ontology.')
        elif upper != '*' and upper < lower:
            ko
            conversion.add_warning(
                property_,
                'This Property has a lower limit of {lower} and an upper '
                    'limit of {upper}. Thus, the domain class of the '
                    'corresponding OWL property is equivalent to '
                    'owl:Nothing (i.e., there must not be any instances '
                    'of the domain class).'
                    .format(**locals()))

        class_uri = conversion.get_element_uri(property_.uml_class)

        graph = self._get_graph_for_standalone_property(
            root_package, conversion, property_)


        graph += owlutils.define_property(
            property_uri,
            owl_property_type,
            domain=class_uri,
            range=type_uri,
            min_cardinality=lower,
            max_cardinality=upper)

        return True


    def _convert_non_assoc_property_redefining(
            self, root_package, conversion, property_, is_final_run):
        """:todo Doc:"""
        
        if not is_final_run:
            return False
        
        assert property_.uml_name == 'Value'

        for redefined_property in property_.uml_redefinedProperty:
            assert redefined_property.uml_name == 'Value'
            continue
            if redefined_property not in conversion.uri_by_element:
                if is_final_run:
                    conversion.add_warning(
                        property_,
                        '''This Property has been skipped because at least one
                            the Properties that it redefines has not been
                            converted (e.g., because it is not in scope or
                            because it has been skipped).''')
                    return True
                else:
                    return False

        redefined_property_closure = closure(
            [property_],
            uml.Property.uml_redefinedProperty.get)
        redefined_property_closure.discard(property_)
        assert redefined_property_closure == set((redefined_property, ))
        root_properties = [
            redefined_prop for redefined_prop in redefined_property_closure
            if not redefined_prop.uml_redefinedProperty] # TODO test 2
        assert root_properties== [redefined_property]
        if len(root_properties) > 1:
            TODO
            
        property_uri = conversion.get_element_uri(root_properties[0])              

        class_generals = self._get_generals_in_scope(
            conversion, property_.uml_class)
        if not class_generals.issuperset(
                redefined_property.uml_class
                for redefined_property in redefined_property_closure):
            conversion.add_warning(
                property_,
                'This Property has been skipped because it redefines a '
                    'Property whose class is not a superclass of this '
                    'Property\'s class.')
            ko
            return True
        class_uri = conversion.get_element_uri(property_.uml_class)
        
        class_specializations = closure(
            [property_.uml_class],
            uml.A_superClass_class.uml_class.get)
        
        # raise Exception(class_specializations)

        # TODO: test empty name
        if property_.uml_name is None:
            WARNING
        else:
            for redefined_property in property_.uml_redefinedProperty:
                if (redefined_property.uml_name is not None
                        and property_.uml_name != redefined_property.uml_name):
                    
                    WARNINGSKIP
                    return True
    
        type_uri, owl_property_type = (
            self._get_type_uri_and_owl_property_type_for_non_assoc_property(
                conversion, property_, redefined_property_closure))
        if (type_uri, owl_property_type) == (None, None):
            return ko
        assert type_uri and owl_property_type
        # TODO: check type consistent?
        # Skip type if inherited.
        if any(property_.uml_type == redefined_property.uml_type
                for redefined_property in redefined_property_closure):
            type_uri = None

        inherited_lowers = set(
            redefined_property.uml_lower
            for redefined_property in redefined_property_closure)
        if property_.uml_lower < max(inherited_lowers):
            conversion.add_warning(
                property_,
                'The lower limit of this Property has been ignored because it '
                    'is not consistent with the lower limits of the redefined '
                    'Properties.')
            lower = None
        elif property_.uml_lower in inherited_lowers:
            lower = None
        else:
            lower = property_.uml_lower

        inherited_uppers = set(
            redefined_property.uml_upper
            for redefined_property in redefined_property_closure)
        if property_.uml_upper == '*':
            if inherited_uppers != {'*'}:
                conversion.add_warning(
                    property_,
                    'The upper limit of this Property is not consistent with '
                    'the upper limits of the redefined Properties.')
            upper = None
        else:
            inherited_uppers.discard('*')
            if inherited_uppers and property_.uml_upper > min(inherited_uppers):
                conversion.add_warning(
                    property_,
                    'The upper limit of this Property has been ignored because '
                        'it is not consistent with the upper limits of the '
                        'redefined Properties.')
                upper = None
            elif property_.uml_upper in inherited_uppers:
                upper = None
            else:
                upper = property_.uml_upper



        # TODO: refactor with non-redef version?
        # TODO: test both checks: the one below, the zero test which should not trigger here
        if (property_.uml_upper != '*'
                and property_.uml_upper < property_.uml_lower):
            conversion.add_warning(
                property_,
                'This Property has a lower limit of {property_.uml_upper} and an upper '
                    'limit of {property_.uml_upper}. Thus, the domain class of the '
                    'corresponding OWL property is equivalent to '
                    'owl:Nothing (i.e., there must not be any instances '
                    'of the domain class).'
                    .format(**locals()))


        conversion.register_element(property_, None)
        
                
            
# TODO: see also Property::isConsistentWith
            
# TODO: test prop redefines itself!
        

        # TODO: check consistency
        #       - check name
        #       - within prop (like in sibling method)
        #       - with redefined classes



        graph = self._get_graph_for_non_assoc_property_redefining(
            root_package, conversion, property_)

        graph += owlutils.restrict_class_on_property(
            class_uri,
            property_uri,
            owl_property_type,
            all_values_from=type_uri,
            min_cardinality=lower,
            max_cardinality=upper)

        return True


    def _get_type_uri_and_owl_property_type_for_non_assoc_property(
            self, conversion, property_, redefined_property_closure):
        # pylint: disable=invalid-name
        """:todo Doc:"""

        type_ = property_.uml_type
        if not type_:
            assert property_.uml_owner.uml_name == 'CustomAttribute'
            #raise Exception(property_.uml_name)
           # conversion.add_warning(
            #    property_,
            #    'This Property has been skipped because no type is given.')
            return None, OWL.ObjectProperty
        elif 0 and isinstance(type_, uml.PrimitiveType):
            ko
            type_uri = self._owl_type_by_uml_primitive_type.get(type_)
            if type_uri:
                if any(redefined_property.uml_type != type_
                        for redefined_property in redefined_property_closure):
                    conversion.add_warning(
                        property_,
                        'This Property has been skipped because its type is '
                            'not consistent with the types of its redefined '
                            'Properties.')
                    return None, None
                return type_uri, OWL.DatatypeProperty
            else:
                conversion.add_warning(
                    property_,
                    'This Property has been skipped because no OWL translation '
                        'for its type is known.')
                return None, None
        elif 1:#type_is(type_, (uml.Class, uml.Enumeration)):
            type_uri = conversion.get_element_uri(type_)
            assert type_uri
            if type_uri:
                if redefined_property_closure:
                    type_generals = self._get_generals_in_scope(
                        conversion, type_)
                    redefined_types = {
                        redefined_property.uml_type
                        for redefined_property in redefined_property_closure}
                    redefined_types.discard(None)
                    if not type_generals.issuperset(redefined_types):
                        print('---', ', '.join(t.uml_name for t in redefined_types))
                        print('---', ', '.join(t.uml_name for t in type_generals))
                        conversion.add_warning(
                            property_,
                            'This Property has been skipped because its type '
                                'is not consistent with the types of its '
                                'redefined Properties.')
                        return None, None
                return type_uri, OWL.ObjectProperty
            else:
                ko
                conversion.add_warning(
                    property_,
                    'This Property has been skipped because its type is not in '
                        'the scope of the OWL conversion (e.g., because it is '
                        'in a Package that is not converted).')
                return None, None
        else:
            raise Exception(type_)
            conversion.add_warning(
                property_,
                'This Property has been skipped because its type is not '
                'supported by this UML2OWL converter.')
            return None, None



        
        
        
        
    def _convert_properties_of_association(self, root_package, conversion, association, is_final_run):
        # TODO: ok???
        for prop in association.uml_memberEnd:
            assert prop.uml_name
            return self._convert_non_assoc_property(root_package, conversion, prop, is_final_run)
            break
        
        return True


    def _get_generals_in_scope(self, conversion, classifier):
        #assert type_is(classifier, (uml.Class, uml.Enumeration))
        return closure(
            [classifier],
            lambda classifier: [
                generalization.uml_general
                for generalization in classifier.uml_generalization
                if generalization in conversion.uri_by_element])        
        

    def _complete_non_assoc_property(self, prop):
         
        if prop.uml_subsettedProperty:
            TODO
             
        if prop.uml_redefinedProperty:
            # TODO: closure
            prop_uris = set(
                self._get_element_uri(redefined_prop, required=False)
                for redefined_prop in prop.uml_redefinedProperty)
            if None in prop_uris:
                # Wait until all redefined properties are complete.
                return False
            if len(prop_uris) != 1:
                INCONSISTENT_ERROR
            prop_uri = prop_uris.pop()
 
        # TODO: move
        graph = self._get_target_graph(prop.uml_owner.uml_package)
 
        class_ = prop.uml_owner
        assert isinstance(class_, uml.Class)
        class_uri = self._get_element_uri(class_)
 
        type_ = prop.uml_type
        # TODO: move
        if isinstance(type_, (uml.Enumeration, uml.Class)):
            type_uri = self._get_element_uri(type_)
        else:
            type_uri = {
                uml.String: XSD.string,
                uml.Integer: XSD.integer,
                uml.Real: XSD.double}.get(type_)
            if not type_uri:
                raise Exception(type_.uml_name, prop.uml_name)
 
        if not prop.uml_redefinedProperty:
            prop_uri = self._new_property_uri(prop)
            self._set_element_uri(prop, prop_uri)
            if isinstance(prop.uml_type, uml.Enumeration):
                owl_type = OWL.ObjectProperty
            else:
                owl_type = OWL.DatatypeProperty
            rdfutils.add_predicates_objects(graph, prop_uri, [
                (RDF.type, owl_type),
                (RDFS.domain, class_uri),
                (RDFS.range, type_uri)])
 
        # TODO: special case lower == upper
        restrict_all_values_from(graph, class_uri, prop_uri, type_uri)
        if prop.uml_lower > 0:
            restrict_min_cardinality(graph, class_uri, prop_uri, prop.uml_lower)
        if prop.uml_upper != '*':
            restrict_max_cardinality(graph, class_uri, prop_uri, prop.uml_upper)
             
        if isinstance(type_, (uml.Enumeration, uml.Class)):
            # TODO: other graph?
            restrict_all_values_from(graph, type_uri, prop_uri, class_uri, inverse=True)
 
 
        return True

                
                
        
        

                                    


########













        


        
        




        



    # TODO END OK

# 
#     def _complete_properties(self):
#         """:todo Doc:"""
# 
#         to_visit = set(self._properties)
#         while to_visit:
#             next_to_visit = set()
#             for prop in to_visit:
#                 if not self._complete_property(prop):
#                     next_to_visit.add(prop)
#             if len(next_to_visit) == len(to_visit):
#                 NOPROGRESSERROR
#             to_visit = next_to_visit
# 
# 
#     def _complete_property(self, prop):
#         """:todo Doc:"""
#         
#         if prop.uml_association:
#             return self._complete_assoc_property(prop)
#         else:
#             return self._complete_non_assoc_property(prop)
#         
#     def _complete_assoc_property(self, prop):
# 
#         assoc = prop.uml_association
# 
#         index = assoc.uml_memberEnd.index(prop)
#         assert index in [0, 1]
#         if index != 0:
#             return True
#         
#         # TODO: use uml api
#         opposite = assoc.uml_memberEnd[1-index]
#         
#         if prop.uml_subsettedProperty or opposite.uml_subsettedProperty:
#             TODO
#             
#         if prop.uml_redefinedProperty:
#             COV
#             if len(prop.uml_redefinedProperty) > 1:
#                 TODO
#             # TODO: closure
#             
#             redefined_prop = list(prop.uml_redefinedProperty)[0]
#             
#             if redefined_prop.uml_name:
#                 COV
#                 prop_uri = self._get_element_uri(redefined_prop, required=False)
#                 if not prop_uri:
#                     COV
#                     return False
#                 prop_uri_is_inverse = False
#                 COV
#             else:
#                 COV
#                 # TODO: check if assoc.
#                 redefined_opp = [x for x in redefined_prop.uml_owner.uml_memberEnd if x is not redefined_prop][0]
#                 assert redefined_opp.uml_name
#                 prop_uri = self._get_element_uri(redefined_opp, required=False)
#                 if not prop_uri:
#                     COV
#                     return False
#                 COV
#                 prop_uri_is_inverse = True
#                 
#         if opposite.uml_redefinedProperty:
#             TODO 
#             
#         # TODO: move
#         graph = self._get_target_graph(prop.uml_owner.uml_package)
# 
#         class_ = prop.uml_owner
#         assert isinstance(class_, uml.Class)
#         class_uri = self._get_element_uri(class_)
# 
#         type_ = prop.uml_type
#         assert isinstance(class_, uml.Class)
#         type_uri = self._get_element_uri(type_)
#         
#         
#         if not prop.uml_redefinedProperty:
#             
#             if prop.uml_name:
#             
#                 prop_uri = self._new_property_uri(prop)
#                 prop_uri_is_inverse = False
#                 self._set_element_uri(prop, prop_uri)
#                 rdfutils.add_predicates_objects(graph, prop_uri, [
#                     (RDF.type, OWL.ObjectProperty),
#                     (RDFS.domain, class_uri),
#                     (RDFS.range, type_uri)])
#                 
#                 
#                 if graph.identifier.endswith('/dexpi.owl'):
#                     DEXPI = rdflib.Namespace(graph.identifier+self._owl_sep)
#                     if prop.uml_aggregation == uml.AggregationKind.composite:
#                         graph.add((prop_uri, RDFS.subPropertyOf, DEXPI.IsComposedOf))
#                 
#             
#                 
#             else:
#                 TODO
#                 
#         if not opposite.uml_redefinedProperty:
#             
#             if opposite.uml_name:
#                 
#                 TODO
# 
#             else:
#                 opp_uri = prop_uri
#                 opp_uri_is_inverse = True
#                 
#                 
#         # TODO: special case lower == upper
#         restrict_all_values_from(graph, class_uri, prop_uri, type_uri, inverse=prop_uri_is_inverse)
#         if prop.uml_lower > 0:
#             restrict_min_cardinality(graph, class_uri, prop_uri, prop.uml_lower, inverse=prop_uri_is_inverse)
#         if prop.uml_upper != '*':
#             restrict_max_cardinality(graph, class_uri, prop_uri, prop.uml_upper, inverse=prop_uri_is_inverse)
#                  
#                     
#         # TODO: special case lower == upper
#         # TODO: other graph?
#         restrict_all_values_from(graph, type_uri, opp_uri, class_uri, inverse=opp_uri_is_inverse)
#         if opposite.uml_lower > 0:
#             restrict_min_cardinality(graph, type_uri, opp_uri, opposite.uml_lower, inverse=opp_uri_is_inverse)
#         if opposite.uml_upper != '*':
#             restrict_max_cardinality(graph, type_uri, opp_uri, opposite.uml_upper, inverse=opp_uri_is_inverse)                   
# 
# 
#         return True         
#                 
#                 
#             
# 
#         
#         
# 
# 
#         
#                 


#     
#     

# 
# 
#         
#             
#   
#         
#         
# 
#         
#           
#           #  elif isinstance(packaged_element, uml.Class):
#           #      self._on_class(packaged_element)
#                     
#     
# 
# 
# 
#     


#     def _new_property_uri(self, prop):
#         owner = prop.uml_owner
#         namespace = self._get_target_graph(self._get_target_package(owner.uml_package))
#         
#         if isinstance(owner, uml.Class):
#             name = prop.uml_name + '_of_' + owner.uml_name
#         else:
#             TODO  
#             
#         return self._new_uri(name, namespace)

#         
#     def _get_owning_package(self, element):
#         
# 
#         package = element.uml_owner
#         if not isinstance(package, uml.Package):
#             error
#             # TODO?
#             
#         return package
#     
# 
#         

  
#                 
#             
#         
#         
#         
#     def _on_begin_element(self, element):
#         if isinstance(element, uml.Class):
#             self._on_class(element)
#         elif isinstance(element, uml.Property):
#             self._on_property(element)            
#         elif isinstance(element, uml.Enumeration):
#             self._on_enumeration(element)       
# 
#     def _get_graph(self, element):
#         return self._graph
#     
#     def _get_uri(self, element):
#         return getattr(DEXPI, element.uml_name)
#     
#     
#     
#     def _on_property(self, prop):
#         
#         if prop.uml_association:
#             return
#         
#         assert not prop.uml_redefinedProperty, prop.uml_redefinedProperty
#         assert not prop.uml_subsettedProperty, prop.uml_subsettedProperty
#         
#         graph = self._get_graph(prop)
#         uri = self._get_uri(prop) # TODO mangle
#         
#         uri = getattr(DEXPI, prop.uml_name[0].lower() + prop.uml_name[1:])
#         
#         return
#         
#         
#         
#        # TODO assert uri not in self._graph.all_nodes(), uri
#         
# 
#         if isinstance(prop.uml_type, (uml.Class, uml.Enumeration)):
#             owl_type = OWL.ObjectProperty
#             owl_range = self._get_uri(prop.uml_type)
#         else:
#             owl_type = OWL.DatatypeProperty
#             owl_range = {
#                 uml.String: XSD.string,
#                 uml.Integer: XSD.integer,
#                 uml.Real: XSD.double}[prop.uml_type]
#               
#         graph.add((uri, RDF.type, owl_type))
# 
#         owner = prop.uml_owner
#         assert isinstance(owner, uml.Class)
# 
#         restr = rdflib.BNode()
#         self._graph.add((restr, RDF.type, OWL.Restriction))
#         self._graph.add((restr, OWL.onProperty, uri))
#         self._graph.add((restr, OWL.allValuesFrom, owl_range))
#         self._graph.add((self._get_uri(owner), RDFS.subClassOf, restr))
# 
#         upper = prop.uml_upper
#         if upper == '*':
#             pass
#         else:
#             restr = rdflib.BNode()
#             self._graph.add((restr, RDF.type, OWL.Restriction))
#             self._graph.add((restr, OWL.onProperty, uri))
#             self._graph.add((restr, OWL.maxCardinality, rdflib.Literal(upper, datatype=XSD.nonNegativeInteger)))
#             self._graph.add((self._get_uri(owner), RDFS.subClassOf, restr))       
#         
#         
#         
#         
# 
#             
#         
# 
# 
# 
#             
# 
#     def _get_target_graph(self, package):
#         target_package = self._get_target_package(package)
#         target_graph = self._graph_by_package.get(target_package)
#         if not target_graph:
#             uri = self._new_package_uri(target_package)
#             target_graph = rdflib.Graph(identifier=uri, store=self._graph.store)
#             target_graph.add((uri, RDF.type, OWL.Ontology))
#             self._graph_by_package[target_package] = target_graph
#             
#             
#             # TODO: move
#             
#             self._graph.bind(target_package.uml_name, uri+self._owl_sep)
#             
#             if uri.endswith('/dexpi.owl'):
#                 
#                 DEXPI = rdflib.Namespace(uri+self._owl_sep)
#                 
#                 target_graph.add((DEXPI.IsComposedOf, RDF.type, OWL.ObjectProperty))
#                 target_graph.add((DEXPI.IsComposedOf, RDF.type, OWL.InverseFunctionalProperty))
#                 target_graph.add((DEXPI.IsComponentOf, RDF.type, OWL.ObjectProperty))
#                 target_graph.add((DEXPI.IsComponentOf, RDF.type, OWL.FunctionalProperty))                
#                 target_graph.add((DEXPI.IsComposedOf, OWL.inverseOf, DEXPI.IsComponentOf))
# 
#                 
#                 
#                 
# 
#             
#         return target_graph
#             
#             
#                     
# 
# 
#     #    uri = self._new_package_uri(package)
#     #    self._set_element_uri(package, uri)
#         
#       #  package_graph = rdflib.Graph(identifier=uri, store=self._graph.store)
#       #  package_graph.add((uri, RDF.type, OWL.Ontology))
#         
#       #  self._graph_by_package[package] = package_graph
#             
#             
#             
#             
#             
#             
#         
#         
#         
#         
#         
# 
# 
#         
#         
#     def _set_element_uri(self, element, uri):
#         assert element not in self.uri_by_element
#         assert uri not in self._element_by_uri
#         self._element_by_uri[uri] = element
#         self.uri_by_element[element] = uri
#         
#         
# 
#                 
#                 

#                 
#                 
#                 
# 
#          #   super_cls_uri = self.uri_by_element[super_cls] # TODO
#          #   graph.add((cls_uri, RDFS.subClassOf, super_cls_uri))
# 
#         for prop in cls.uml_ownedAttribute:
#             
#             if prop.uml_association:
#                 continue
#             
#             assert not prop.uml_redefinedProperty
#             assert not prop.uml_subsettedProperty
#             
#             
#             
#             continue
#             
#             
#             # TODO: avoid of when possible
#             prop_uri = getattr(DEXPI, prop.uml_name + '_of_' + element.uml_name)
#             assert prop_uri not in self._graph.all_nodes()
#             
#             if prop.uml_type in (unicode, int, float):
#                 prop_type = OWL.DatatypeProperty
#  
#             else:
#                 prop_type = OWL.ObjectProperty
#                 prop_range = cls_uri(prop.uml_type)
#                 if isinstance(prop.uml_type, uml.Class):
#                     pass#TODOCLASS
#                 elif isinstance(prop.uml_type, uml.Enumeration):
#                     pass#TODOCLASS
#                 else:
#                     raise Exception(prop.uml_type)
#                 
#             
#                 
#             self._graph.add((prop_uri, RDF.type, prop_type))
#             self._graph.add((prop_uri, RDFS.domain, cls))
#             self._graph.add((prop_uri, RDFS.range, prop_range))
#             
#             upper = prop.uml_upper
#             if upper == '*':
#                 pass
#             else:
#                 assert isinstance(upper, int) and upper >= 1
#                 restr = rdflib.BNode()
#                 self._graph.add((restr, RDF.type, OWL.Restriction))
#                 self._graph.add((restr, OWL.onProperty, prop_uri))
#                 self._graph.add((restr, OWL.maxCardinality, rdflib.Literal(upper, datatype=XSD.nonNegativeInteger)))
#                 self._graph.add((cls, RDFS.subClassOf, restr))
#                 
# 
#             lower = prop.uml_lower
#             
#             if lower != 0:
#                 assert isinstance(upper, int) and lower >= 0
#                 restr = rdflib.BNode()
#                 self._graph.add((restr, RDF.type, OWL.Restriction))
#                 self._graph.add((restr, OWL.onProperty, prop_uri))
#                 self._graph.add((restr, OWL.minCardinality, rdflib.Literal(lower, datatype=XSD.nonNegativeInteger)))
#                 self._graph.add((cls, RDFS.subClassOf, restr))
#                 
#             if prop.uml_aggregation == 'composite':
#                 self._graph.add((
#                     prop_uri, RDFS.subPropertyOf, BASE.isComposedOf))
#                 
# 
# 
# 
#     
#     def _on_enumeration(self, element):
#         return
#         
#         cls = cls_uri(element)
#         
#         
# 
#         type_triple = (cls, RDF.type, OWL.Class)
#         assert type_triple not in self._graph
#         self._graph.add(type_triple)
#         
#         self._subclasses.setdefault(element, set())
#         
#         lit_uris = set()
# 
#         for lit in element.uml_ownedLiteral:
#             lit_uri = getattr(DEXPI, element.uml_name + '_' + lit.uml_name)
#             self._graph.add((lit_uri, RDF.type, cls))
#             lit_uris.add(lit_uri)
#             
#         assert lit_uris
#         
#         import rdflib.collection
#         
#         lst = rdflib.BNode()
#         
#         
#             
#         rdflib.collection.Collection(
#             self._graph, lst, lit_uris)
#         
#         self._graph.add((cls, OWL.oneOf, lst))
#         
#         all_diff = rdflib.BNode()
#         self._graph.add((all_diff, RDF.type, OWL.AllDifferent))
#         
#         lst = rdflib.BNode()
#         self._graph.add((all_diff, OWL.members, lst))
#         
#         rdflib.collection.Collection(
#             self._graph, lst, lit_uris)
#         



def uml2owl(package, **config):
    converter = Uml2OwlConverter(Uml2OwlConverterConfig(**config))
    return converter.run(package)

def create_owl(element):
    
    
    element.uml_URI = 'http://www.aixcape.org/integration'
    conversion = uml2owl(element)

 #   OwlBuilder(element)

  #  g = rdflib.Graph()
  #  g.add((DEXPI.Equipment, RDF.type, DEXPI.Murks))
  
  
    graph = conversion.owl_graph

   # for context in graph.contexts():
        
    #    print(context)
    write_owl_graphs(graph, r'C:\temp\owl')
    return graph
    


    
def write_owl_graphs(graph, root_dir):
    
    for context in graph.contexts():
        
        # ParseResult(scheme=u'http', netloc=u'www.aixcape.org', path=u'/integration/iso_15926.owl', params='', query='', fragment='')
        parse_result = urlparse.urlparse(context.identifier)
        path_parts = [root_dir, parse_result.netloc] + parse_result.path.split('/')
        path = upath.absjoin(*path_parts)
        assert path.startswith(root_dir)
        upath.makedirs(upath.dirname(path))
        context.serialize(destination=path, format='xml')
        context.serialize(destination=path+'.n3', format='n3')
        g = rdflib.Graph().parse(path+'.n3', format='n3')
        g.serialize(destination=path, format='pretty-xml')
        


        
# TODO: move

def with_indef_article(noun):
    if noun[0].lower() in 'aeiou':
        article = 'an'
    else:
        article = 'a'
    return '{article} {noun}'.format(**locals())
        
        
'''
in DEXPI
--------
            
            if uri.endswith('/dexpi.owl'):
                
                DEXPI = rdflib.Namespace(uri+self._owl_sep)
                
                target_graph.add((DEXPI.IsComposedOf, RDF.type, OWL.ObjectProperty))
                target_graph.add((DEXPI.IsComposedOf, RDF.type, OWL.InverseFunctionalProperty))
                target_graph.add((DEXPI.IsComponentOf, RDF.type, OWL.ObjectProperty))
                target_graph.add((DEXPI.IsComponentOf, RDF.type, OWL.FunctionalProperty))                
                target_graph.add((DEXPI.IsComposedOf, OWL.inverseOf, DEXPI.IsComponentOf))

'''     


def type_is(obj, type_):
    try:
        iter(type_)
        return type(obj) in type_
    except TypeError:
        return type(obj) is type_



def apply_while_progress(items, function):
    progress = True
    while items and progress:
        unhandled_items = []
        for item in items:
            item_progress = function(item)
            assert isinstance(item_progress, bool)
            if not item_progress:
                unhandled_items.append(item)
        progress = len(unhandled_items) < len(items)
        items = unhandled_items
    return items


def closure(values, getter):
    
    visited = set()
    to_visit = set(values)
    
    while to_visit:
        item = to_visit.pop()
        visited.add(item)
        to_visit.update(set(getter(item)).difference(visited))
        
    return visited








class AttributeList(list):
    pass


def a_class(node):
    return [(node, RDF.type, OWL.Class)]

def complement_of(cls, other):
    return [(cls, OWL.complementOf, other)]

def a_named_individual(node, class_=None):
    result = [(node, RDF.type, OWL.NamedIndividual)]
    if class_ is not None:
        result += [(node, RDF.type, class_)]
    return result
        

def a(node, node_type):
    return [(node, RDF.type, node_type)]

def sub_class_of(sub_class, super_class):
    return [(sub_class, RDFS.subClassOf, super_class)]



def sub_property_of(sub_class, super_class):
    return [(sub_class, RDFS.subPropertyOf, super_class)]






def equivalent_class(class_1, class_2):
    return [(class_1, OWL.equivalentClass, class_2)]

def equivalent_union(class_, sub_classes):
    union_of_result = union_of(sub_classes)
    result = (
        union_of_result +
        equivalent_class(class_, union_of_result.class_))
    return result

def equivalent_one_of(class_, individuals):
    one_of_result = one_of(individuals)
    result = (
        one_of_result +
        equivalent_class(class_, one_of_result.class_))
    return result

def all_different(individuals):
    all_different = rdflib.BNode()
    individual_list = rdflist(individuals)
    result = [(all_different, OWL.distinctMembers, individual_list.first)]
    result += a(all_different, OWL.AllDifferent)
    result += individual_list
    return result

def union_of(classes):
    class_ = rdflib.BNode()
    class_list = rdflist(classes)
    result = AttributeList(itertools.chain(
        a(class_, OWL.Class),
        [(class_, OWL.unionOf, class_list.first)],
        class_list))
    result.class_ = class_
    return result


def intersection_of(classes):
    class_ = rdflib.BNode()
    class_list = rdflist(classes)
    result = AttributeList(itertools.chain(
        a(class_, OWL.Class),
        [(class_, OWL.intersectionOf, class_list.first)],
        class_list))
    result.class_ = class_
    return result

def one_of(individuals):
    class_ = rdflib.BNode()
    individual_list = rdflist(individuals)
    result = AttributeList(itertools.chain(
        a(class_, OWL.Class),
        [(class_, OWL.oneOf, individual_list.first)],
        individual_list))
    result.class_ = class_
    return result
       
def rdflist(items):
    result = AttributeList()
    first_node = None
    prev_node = None
    for item in items:
        node = rdflib.BNode()
        if prev_node:
            result.append((prev_node, RDF.rest, node))
        else:
            first_node = node
        prev_node = node
        result.append((node, RDF.first, item))
    if first_node:
        result.first = first_node
        result.append((node, RDF.rest, RDF.nil))
    else:
        result.first = RDF.nil
    return result
        
        
        
def all_disjoint_classes(classes):
    axiom = rdflib.BNode()
    members = rdflist(classes)
    result = a(axiom, OWL.AllDisjointClasses)
    result.append((axiom, OWL.members, members.first))
    result.extend(members)
    return result
    
    result.extend()
    
    
    
    
def restrict_some_values_from(restricted_class, prop, property_type, values_class, inverse=False):
    return _restrict_property(restricted_class, prop, property_type, [(OWL.someValuesFrom, values_class)], inverse)

def restrict_all_values_from(restricted_class, prop, property_type, values_class, inverse=False):
    return _restrict_property(restricted_class, prop, property_type, [(OWL.allValuesFrom, values_class)], inverse)

def restrict_cardinality(restricted_class, prop, property_type, cardinality, inverse=False):
    return _restrict_property(restricted_class, prop, property_type, [(OWL.cardinality, rdflib.Literal(cardinality, datatype=rdflib.XSD.nonNegativeInteger))], inverse)

def restrict_min_cardinality(restricted_class, prop, property_type, min_cardinality, inverse=False):
    return _restrict_property(restricted_class, prop, property_type, [(OWL.minCardinality, rdflib.Literal(min_cardinality, datatype=rdflib.XSD.nonNegativeInteger))], inverse)
     
def restrict_max_cardinality(restricted_class, prop, property_type, max_cardinality, inverse=False):
    return _restrict_property(restricted_class, prop, property_type,
        [(OWL.maxCardinality, rdflib.Literal(max_cardinality, datatype=rdflib.XSD.nonNegativeInteger))], inverse)
    
def restrict_max_cardinality_qualified(restricted_class, prop, property_type, max_cardinality, qualified_type, inverse=False):
    return _restrict_property(restricted_class, prop, property_type,
        [(OWL.maxQualifiedCardinality, rdflib.Literal(max_cardinality, datatype=rdflib.XSD.nonNegativeInteger)),
         (OWL.onClass, qualified_type)], inverse)
    
def restrict_min_cardinality_qualified(restricted_class, prop, property_type, min_cardinality, qualified_type, inverse=False):
    return _restrict_property(restricted_class, prop, property_type,
        [(OWL.minQualifiedCardinality, rdflib.Literal(min_cardinality, datatype=rdflib.XSD.nonNegativeInteger)),
         (OWL.onClass, qualified_type)], inverse)
    
    
def restrict_cardinality_qualified(restricted_class, prop, property_type, cardinality, qualified_type, inverse=False):
    return _restrict_property(restricted_class, prop, property_type,
        [(OWL.cardinality, rdflib.Literal(cardinality, datatype=rdflib.XSD.nonNegativeInteger)),
         (OWL.onClass, qualified_type)], inverse)
    
    
    
def _restrict_property(restricted_class, prop, property_type, restriction_props, inverse):
    
    assert property_type in (OWL.DatatypeProperty, OWL.ObjectProperty)
    
    result = []

    if inverse:
        inv_prop = rdflib.BNode()
        result += a(inv_prop, OWL.DatatypeProperty)
        result.append((inv_prop, OWL.inverseOf, prop))
        prop = inv_prop

    restriction = rdflib.BNode()
    result += [
        (restriction, RDF.type, OWL.Restriction),
        (restricted_class, RDFS.subClassOf, restriction),
        (restriction, OWL.onProperty, prop)]
    for pred, obj in restriction_props:
        result.append((restriction, pred, obj))
        
    return result    
               


def restrict_class_on_property(
        class_node, property_node, property_type, all_values_from=None,
        min_cardinality=None, max_cardinality=None, max_symbols=(None, '*')):
    
    result = []
    
    if all_values_from is not None:
        result += restrict_all_values_from(class_node, property_node, property_type, all_values_from)
        
    if min_cardinality is not None:
        checks.check_non_negative_integer(min_cardinality)
    if max_cardinality in max_symbols:
        max_cardinality = None
    elif max_cardinality is not None:
        checks.check_non_negative_integer(max_cardinality)
        
    if None != min_cardinality == max_cardinality:
        result += restrict_cardinality(class_node, property_node, property_type, min_cardinality)
    else:
        if min_cardinality is not None and min_cardinality > 0:
            result += restrict_min_cardinality(class_node, property_node, property_type, min_cardinality)
        if max_cardinality is not None:
            result += restrict_max_cardinality(class_node, property_node, property_type, max_cardinality)            

    return result
        


def define_property(node, property_type, domain=None, range=None, min_cardinality=None,
        max_cardinality=None, max_symbols=(None, '*'), verbose=False):
    
    result = a(node, property_type)
    if domain is not None:
        result.append((node, RDFS.domain, domain))
    if range is not None:
        result.append((node, RDFS.range, range))
    if min_cardinality is not None:
        checks.check_non_negative_integer(min_cardinality, 'min_cardinality')
    if max_cardinality in max_symbols:
        max_cardinality = None
    else:
        checks.check_non_negative_integer(max_cardinality, 'max_cardinality')
    if min_cardinality == max_cardinality != None:
        # Case min_cardinality == max_cardinality == 1 is excluded; it will be
        # written using owl:FunctionalProperty and a min. cardinalty instead.
        result.extend(restrict_cardinality(domain, node, property_type, min_cardinality))
    elif 0 and max_cardinality == 1:
        result += a(node, OWL.FunctionalProperty)
        if min_cardinality > 0:
            result += restrict_min_cardinality(domain, node, property_type, min_cardinality)
    else:
        if domain is None:
            ERROR # using owl:Thing instead ok? check before if?     
        if min_cardinality > 0:
            result.extend(restrict_min_cardinality(domain, node, property_type, min_cardinality))
        if max_cardinality is not None:
            result.extend(restrict_max_cardinality(domain, node, property_type, max_cardinality))            
            

   # g = rdflib.Graph()
   # g += result
   # print(g.serialize())
    #kp

    return result