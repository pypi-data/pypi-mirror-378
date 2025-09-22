from copy import deepcopy

class Template_OBO:

    base_template = dict(
        pid=None,
        role_type="http://purl.obolibrary.org/obo/OBI_0000093",
        process_type=None,
        attribute_type=None,
        organisation_id=None,
        organisation_type=None,
        input_type=None,
        target_type=None,
        output_type=None,
        output_id=None,
        unit_type=None,
        specific_method_type=None,
        protocol_type=None,
        protocol_id=None,
        cause_type=None,
        functional_specification_type=None,
        frequency_type=None,
        frequency_value=None,
        notation_id=None,
        notation_type=None,
        value_date=None,
        value_integer=None,
        value_string=None,
        value_float=None,
        value_datatype=None,
        comments=None,
        startdate=None,
        enddate=None,
        age=None,
        uniqid=None,
        event_id=None,
        value=None,
        valueIRI=None,
        activity=None,
        target=None,
        agent=None,
        input=None,
        unit=None
    )

    @classmethod
    def build_entry(cls, **overrides):
        entry = deepcopy(cls.base_template)
        entry.update(overrides)
        return entry

TEMPLATE_MAP_OBO = {

        "Birthdate": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C68615",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:date"
        ),
        "Birthyear": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C83164",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:integer"
        ),
        "Country": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            output_type="http://purl.obolibrary.org/obo/NCIT_C20108",
            value_datatype="xsd:string"
        ),
        "Deathdate": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C70810",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            protocol_type="http://purl.obolibrary.org/obo/NCIT_C163970",
            value_datatype="xsd:date"
        ),
        "First_visit": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C164021",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:date"
        ),
        "Symptoms_onset": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C124353",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:date"
        ),
        "Sex": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            output_type="http://purl.obolibrary.org/obo/NCIT_C160908",
            value_datatype="xsd:string"
        ),
        "Status": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            output_type="http://purl.obolibrary.org/obo/NCIT_C164628",
            value_datatype="xsd:string"
        ),
        "Diagnosis": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C18020",
            output_type="http://purl.obolibrary.org/obo/NCIT_C154625",
            value_datatype="xsd:string"
        ),
        "Phenotype": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C18020",
            output_type="http://purl.obolibrary.org/obo/NCIT_C164607",
            value_datatype="xsd:string"
        ),
        "Genetic": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C15709",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C45766",
            protocol_type="http://purl.obolibrary.org/obo/NCIT_C171178",
            value_datatype="xsd:string"
        ),
        "Questionnaire": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C95401",
            output_type="http://purl.obolibrary.org/obo/NCIT_C91102",
            protocol_type="http://purl.obolibrary.org/obo/NCIT_C73537",
            value_datatype="xsd:float"
        ),
        "Disability": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C20993",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C21007",
            output_type="http://purl.obolibrary.org/obo/NCIT_C91102",
            protocol_type="http://purl.obolibrary.org/obo/NCIT_C73537",
            value_datatype="xsd:float"
        ),
        "Examination": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/MAXO_0000487",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:float"
        ),
        "Laboratory": Template_OBO.build_entry(
            process_type="http://purl.obolibrary.org/obo/NCIT_C25294",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            value_datatype="xsd:float"
        ),
        "Surgery": Template_OBO.build_entry(
            process_type = "http://purl.obolibrary.org/obo/NCIT_C15329",
            value_datatype = "xsd:string"
        ),
        "Hospitalization": Template_OBO.build_entry(
            process_type = "http://purl.obolibrary.org/obo/NCIT_C25179",
            value_datatype = "xsd:string"
        ),
        "Prescription": Template_OBO.build_entry(
            process_type = "http://purl.obolibrary.org/obo/NCIT_C70962",
            protocol_type = "http://purl.obolibrary.org/obo/PDRO_0000191",        
            notation_type = "http://purl.obolibrary.org/obo/NCIT_C177929",      
            output_type = "http://purl.obolibrary.org/obo/NCIT_C198143",
            value_datatype = "xsd:float"
        ),
        "Medication": Template_OBO.build_entry(
            process_type = "http://purl.obolibrary.org/obo/NCIT_C70962",
            protocol_type = "http://purl.obolibrary.org/obo/PDRO_0010022",        
            notation_type = "http://purl.obolibrary.org/obo/NCIT_C177929",      
            output_type = "http://purl.obolibrary.org/obo/NCIT_C167190",
            value_datatype = "xsd:float"
        ),
        "Clinical_trial": Template_OBO.build_entry(
            process_type = "http://purl.obolibrary.org/obo/NCIT_C71104",
            organisation_type = "http://purl.obolibrary.org/obo/NCIT_C16696",
            output_type = "http://purl.obolibrary.org/obo/NCIT_C115575", 
            value_datatype = "xsd:string"
        ),
        "Biobank": Template_OBO.build_entry(
            process_type = "http://purl.obolibrary.org/obo/OMIABIS_0000061",
            organisation_type = "http://purl.obolibrary.org/obo/OBIB_0000616",
            output_type = "http://purl.obolibrary.org/obo/NCIT_C115570", 
            output_id_type = "http://purl.obolibrary.org/obo/NCIT_C25364",
            value_datatype = "xsd:string"
        ),
    }

class Template_SNOMED:

    base_template = dict(
        pid=None,
        role_type="http://snomed.info/id/116154003",
        process_type=None,
        attribute_type=None,
        organisation_id=None,
        organisation_type=None,
        input_type=None,
        target_type=None,
        output_type=None,
        output_id=None,
        unit_type=None,
        specific_method_type=None,
        protocol_type=None,
        protocol_id=None,
        cause_type=None,
        functional_specification_type=None,
        frequency_type=None,
        frequency_value=None,
        notation_id=None,
        notation_type=None,
        value_date=None,
        value_integer=None,
        value_string=None,
        value_float=None,
        value_datatype=None,
        comments=None,
        startdate=None,
        enddate=None,
        age=None,
        uniqid=None,
        event_id=None,
        value=None,
        valueIRI=None,
        activity=None,
        target=None,
        agent=None,
        input=None,
        unit=None
    )

    @classmethod
    def build_entry(cls, **overrides):
        entry = deepcopy(cls.base_template)
        entry.update(overrides)
        return entry

TEMPLATE_MAP_SNOMED = {
        "Birthdate": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/312486000",
            attribute_type="http://snomed.info/id/3950001",
            output_type="http://snomed.info/id/184099003",
            value_datatype="xsd:date"
        ),
        "Birthyear": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/312486000",
            attribute_type="http://snomed.info/id/3950001",
            output_type="http://snomed.info/id/258707000",
            value_datatype="xsd:integer"
        ),
        "Deathdate": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/363049002",
            attribute_type="http://snomed.info/id/419620001",
            output_type="http://snomed.info/id/399753006",
            value_datatype="xsd:date"
        ),
        "First_visit": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/308335008",
            attribute_type="http://snomed.info/id/769681006",
            output_type="http://snomed.info/id/406543005",
            value_datatype="xsd:date"
        ),
        "Symptoms_onset": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/308335008",
            attribute_type="http://snomed.info/id/308918001",
            output_type="http://snomed.info/id/298059007",
            value_datatype="xsd:date"
        ),
        "Sex": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/363306006",
            output_type="http://snomed.info/id/734000001",
            value_datatype="xsd:string"
        ),
        "Status": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/386053000",
            output_type="http://snomed.info/id/420107008",
            value_datatype="xsd:string"
        ),
        "Diagnosis": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/103693007",
            output_type="http://snomed.info/id/439401001",
            value_datatype="xsd:string"
        ),
        "Phenotype": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/363778006",
            output_type="http://snomed.info/id/363788007",
            value_datatype="xsd:string"
        ),
        "Genetic": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/405824009",
            output_id_type="http://snomed.info/id/118522005",
            value_datatype="xsd:string"
        ),
        "Disability": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/81078003",
            attribute_type="http://snomed.info/id/21134002",
            output_type="http://snomed.info/id/273421001",
            value_datatype="xsd:float"
        ),
        "Corporal": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/54709006",
            output_type="http://snomed.info/id/248326004",
            value_datatype="xsd:float"
        ),
        "Laboratory": Template_SNOMED.build_entry(
            process_type="http://snomed.info/id/108252007",
            output_type="http://snomed.info/id/275924004",
            protocol_type="http://snomed.info/id/258049002",
            value_datatype="xsd:float"
        ),
        "Surgery": Template_SNOMED.build_entry(
            process_type = "http://snomed.info/id/387713003",
            protocol_type = "http://snomed.info/id/258049002",        
            value_datatype = "xsd:string"
        ),
        "Medication": Template_SNOMED.build_entry(
            process_type = "http://snomed.info/id/18629005",
            protocol_type = "http://snomed.info/id/260885003",        
            substance_type = "http://snomed.info/id/246488008",      
            concentration_type = "http://snomed.info/id/3317411000001100",
            value_datatype = "xsd:float"
        ),
        "Clinical_trial": Template_SNOMED.build_entry(
            process_type = "http://snomed.info/id/NCIT_C71104",
            organization_type = "http://snomed.info/id/22232009",
            output_type = "http://snomed.info/id/229059009", 
            value_datatype = "xsd:string"
        )
    }