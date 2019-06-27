from contracting_process.processor import get_value

item = {
    "id": "123",
    "tender": {
        "id": "0rw29R-005-2011-1",
        "items": [
            {
                "id": "0rw29R005-2011197482",
                "unit": {"name": "Unidad"},
                "quantity": 4.0,
                "description": "Llanta para vehiculo # 235/75R15 radiales de 8 o 10 lonas",
                "classification": {
                    "id": "25171901",
                    "scheme": "UNSPSC",
                    "description": "Llantas y rines para automóviles"
                }
            }
        ],
    },
    "parties": [
        {
            "id": "7rBOL0",
            "name": "Secretaria de Desarrollo Economico",
            "roles": ["buyer"],
            "address": {
                "streetAddress": "Edificio San José,3 piso Boulevard KUWAIT "
            },
            "identifier": {"scheme": "HN-ONCAE-CE"},
            "contactPoint": {
                "url": "http://www.sic.gob.hn",
                "email": "2235-3678",
                "faxNumber": "2235-5037"
            }
        },
        {
            "id": "0rw29R-7rBOL0",
            "name": "Unidad Central",
            "roles": ["buyer"],
            "address": {
                "region": "Francisco Morazan",
                "locality": "DISTRITO CENTRAL",
                "streetAddress": "Edificio San José Boulevard KUWAIT 3 piso FENADUANAH"
            },
            "memberOf": [
                {"id": "7rBOL0", "name": "Secretaria de Desarrollo Economico"}
            ],
            "identifier": {"scheme": "HN-ONCAE-CE"},
            "contactPoint": {
                "url": "http://www.sic.gob.hn",
                "name": "Ranulfo Reyes Ramírez ",
                "email": "sonalfa@sic.gob.hn, arojas@sic.gob.hn, rreyes@sic.gob.hn",
                "faxNumber": "235-5037",
                "telephone": "235-5037"
            }
        }
    ],
    "sources": [
        {
            "id": "honducompras-1",
            "url": "http://h1.honducompras.gob.hn/",
            "name": "HonduCompras 1.0 - Módulo de Difusión de Compras y Contrataciones"
        }
    ],
}


def test_get_value():
    assert get_value(item, ["id"]) == "123"
