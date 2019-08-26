import functools

from contracting_process.resource_level.consistent.org_ref_name import \
    calculate
from tools.checks import get_empty_result_resource

"""
author: Iaroslav Kolodka

The file contains part of the tests for the
 contracting_process.resource_level.consistent.org_ref_name.calculate function .

"""


version = "1.0"

calculate_prepared = functools.partial(
    calculate,
    path="awards.suppliers"
)

suppliers_item_ok = {
    "parties": [
        {
            "id": "111",
            "name": "bbb",
        },
        {
            "id": "000",
            "name": "aaa",
        }
    ],
    "awards": [
        {
            "suppliers": [
                {
                    "id": "000",
                    "name": "aaa"
                },
                {
                    "id": "111",
                    "name": "bbb"
                }

            ]
        }
    ]
}
suppliers_item_fail_partially = {
    "parties": [
        {
            "id": "111",
            "name": "bbb",
        },
        {
            "id": "000",
            "name": "aaa",
        }
    ],
    "awards": [
        {
            "suppliers": [
                {
                    "id": "000",
                    "name": "aaa"
                },
                {
                    "id": "111",
                    "name": "ccc"  # wrong
                }

            ]
        }
    ]
}


def test_fail():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = False
    expected_result["value"] = None
    expected_result["application_count"] = 2
    expected_result["pass_count"] = 1
    expected_result["meta"] = {
        "references": [
            {
                "organization_id": "000",
                "expected_name": "aaa",
                "referenced_party_path": "parties[1]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "awards[0].suppliers[0]",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            },
            {
                "organization_id": "111",
                "expected_name": "ccc",
                "referenced_party_path": "parties[0]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "awards[0].suppliers[1]",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            }
        ]
    }
    result = calculate_prepared(suppliers_item_fail_partially)
    assert result == expected_result


def test_ok():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = True
    expected_result["value"] = None
    expected_result["application_count"] = 2
    expected_result["pass_count"] = 2
    expected_result["meta"] = {
        "references": [
            {
                "organization_id": "000",
                "expected_name": "aaa",
                "referenced_party_path": "parties[1]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "awards[0].suppliers[0]",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            },
            {
                "organization_id": "111",
                "expected_name": "bbb",
                "referenced_party_path": "parties[0]",
                # -"referenced_party": buyer_item_ok["parties"][0],
                "resource_path": "awards[0].suppliers[1]",
                # -"resource": buyer_item_ok["buyer"],
                # -"result": True
            }
        ]
    }
    result = calculate_prepared(suppliers_item_ok)
    assert result == expected_result


item_for_big_test = {
    "id": "ocds-k50g02-11-12-475154-2011-04-05T09:23:59.000Z",
    "tag": [
        "compiled"
    ],
    "date": "2011-04-05T09:23:59.000Z",
    "ocid": "ocds-k50g02-11-12-475154",
    "buyer": {
        "id": "800140603",
        "name": "DIRECCIÓN GENERAL DE LA POLICÍA NACIONAL (PONAL)"
    },
    "awards": [
        {
            "id": 519480,
            "title": "12-7-10007-11",
            "value": {
                "amount": 130432400.0,
                "currency": "COP"
            },
            "status": "active",
            "suppliers": [
                {
                    "id": "811006026",
                    "name": "INVERSIONES XOS LTDA."
                }
            ],
            # "description": "Objeto: MANTENIMIENTO DE MOTOCICLETAS ASIGNADOS
            #  A LA POLICIA METROPOLITANA DEL VALLE DE ABURRA Y POLICIA FISCAL
            #  ADUANERA REGIONAL MEDELLIN Calificación definitiva: No definido",
            "contractPeriod": {
                "startDate": "2011-04-04T00:00:00.000Z",
                "durationInDays": 270
            }
        }
    ],
    "tender": {
        "id": "11-12-475154",
        "title": "PN MEVAL CD 008 2011",
        "value": {
            "amount": 130432400.0
        },
        "status": "complete",
        "coveredBy": [
            "x_Estatuto_General_de_Contratación"
        ],
        "milestones": [
            {
                "id": 1,
                "type": "preProcurement",
                "title": "Apertura",
                "status": "scheduled"
            }
        ],
        # "description": "MANTENIMIENTO DE MOTOCICLETAS ASIGNADOS A LA POLICIA
        #  METROPOLITANA DEL VALLE DE ABURRA Y POLICIA FISCAL ADUANERA REGIONAL MEDELLIN",
        "procuringEntity": {
            "id": "800140603",
            "name": "DIRECCIÓN GENERAL DE LA POLICÍA NACIONAL (PONAL)"
        },
        "submissionMethod": [
            "inPerson"
        ],
        "expressionAddress": {
            "countryName": "Colombia"
        },
        "procurementMethod": "limited",
        # "submissionMethodDetails": "Municipio obtención: No definido Municipio
        #  entrega: No definido Municipio ejecución: Antioquia - Medellín Lugar aclaraciones: No definido",
        "procurementMethodDetails": "Contratación Directa (Ley 1150 de 2007)",
        # "procurementMethodRationale": "Contratación de Bienes y Servicios en e
        # l Sector Defensa y en el DAS (Literal D)"
    },
    "parties": [
        {
            "id": "800140603",
            "name": "DIRECCIÓN GENERAL DE LA POLICÍA NACIONAL (PONAL)",
            "roles": [
                "procuringEntity",
                "buyer",
                "payer"
            ],
            "address":{
                "region": "Bogotá D.C.",
                "locality": "Bogotá D.C.",
                "countryName": "COLOMBIA",
                "streetAddress": "Transversal 45  40 - 11  CAN"
            },
            "details": {
                "level": "NACIONAL",
                "order": "NACIONAL CENTRALIZADO"
            },
            "identifier": {
                "id": "800140603",
                "scheme": "CO-RUE",
                "legalName": "DIRECCIÓN GENERAL DE LA POLICÍA NACIONAL (PONAL)"
            },
            "contactPoint": {
                "name": "ILIANA YANETT OBANDO VELASQUEZ",
                "email": "gadmimveal@policia.gov.co",
                "telephone": "(4) 5145155 - 514 61 63"
            }
        },
        {
            "id": "811006026",
            "name": "INVERSIONES XOS LTDA.",
            "roles": [
                "supplier",
                "payee"
            ],
            "address":{
                "region": " Colombia",
                "locality": "Antioquia",
                "countryName": "COLOMBIA",
                "streetAddress": "CALLE 38  52-73"
            },
            "identifier": {
                "id": "811006026",
                "scheme": "CO-RUE",
                "legalName": "INVERSIONES XOS LTDA."
            },
            "contactPoint": {
                "name": "JULIAN ENRIQUE MONTOYA RODRIGUEZ"
            },
            "additionalContactPoint": {
                "identifier": {
                    "id": "811006026",
                    "scheme": "COL-IDCARD",
                    "legalName": "JULIAN ENRIQUE MONTOYA RODRIGUEZ"
                }
            }
        }
    ],
    "language": "es",
    "planning": {
        # "rationale": "MANTENIMIENTO DE MOTOCICLETAS ASIGNADOS A LA POLICIA METROPOLITANA DEL
        #  VALLE DE ABURRA Y POLICIA FISCAL ADUANERA REGIONAL MEDELLIN",
        "milestones": [
            {
                "id": 1,
                "type": "preProcurement",
                "title": "Apertura",
                "status": "scheduled"
            }
        ]
    },
    "contracts": [
        {
            "id": 519480,
            "title": "12-7-10007-11",
            "value": {
                "amount": 130432400.0,
                "currency": "COP"
            },
            "period": {
                "startDate": "2011-04-04T00:00:00.000Z",
                "durationInDays": 270
            },
            "awardID": 519480,
            "amendments": [
                {
                    "id": "1084360",
                    "date": "2011-08-22T09:58:32.000Z",
                    "description": "Adición al contrato"
                }
            ],
            "dateSigned": "2011-03-31T00:00:00.000Z",
            # "description": "MANTENIMIENTO DE MOTOCICLETAS ASIGNADOS A LA POLICIA METROPOLITANA DEL VALLE DE ABURRA Y
            #  POLICIA FISCAL ADUANERA REGIONAL MEDELLIN"
        }
    ],
    "lastUpdate": "2019-05-20T16:58:12.000Z",
    "initiationType": "tender"
}


def test_big():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = True
    expected_result["value"] = None
    expected_result["application_count"] = 1
    expected_result["pass_count"] = 1
    expected_result["meta"] = {
        "references": [
            {
                "expected_name": "INVERSIONES XOS LTDA.",
                "resource_path": "awards[0].suppliers[0]",
                "organization_id": "811006026",
                "referenced_party_path": "parties[1]"
            }
        ]
    }
    result = calculate_prepared(item_for_big_test)
    assert result == expected_result


item_party_not_found = {
    "parties": [
        {
            "id": "111",
            "name": "bbb",
        },
        {
            "id": "222",
            "name": "aaa",
        }
    ],
    "awards": [
        {
            "suppliers": [
                {
                    "id": "000",
                    "name": "aaa"
                }
            ]
        }
    ]

}


def test_party_not_found():
    expected_result = get_empty_result_resource(version)
    expected_result["result"] = None
    expected_result["value"] = None
    expected_result["application_count"] = 0
    expected_result["pass_count"] = 0
    expected_result["meta"] = {
        "reason": "there are no values with check-specific properties"
    }
    result = calculate_prepared(item_party_not_found)
    assert result == expected_result
