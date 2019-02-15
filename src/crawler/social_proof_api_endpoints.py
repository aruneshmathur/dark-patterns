# Make sure add a name
# Add the request body as a JSON string
# Use https://jsoneditoronline.org/ to validate and format the string

ENDPOINTS = [
    {
        "name": "QUBIT_TKMAXX_1",
        "method": "GET",
        "url": "https://tally-1.qubitproducts.com/tally/tk_maxx/ecount/t098-addedToBag/94015569"
    },
    {
        "name": "SALE_CYCLE_COTTONONUS_1",
        "headers": {"Content-Type": "text/plain; charset=UTF-8"},
        "url": "https://c.salecycle.com/osr/config",
        "params": {"msgId": "53e1c7e8-aebf-4a4e-9f1f-80851394c8dc"},
        "body": """{
          "apiKey": "273e5348-41f5-4abb-ba72-1a5046b130db",
          "clientName": "cottononus",
          "templates": [
            {
              "templateId": 7322,
              "type": "BrandEnforcement",
              "metrics": {
                "key": "productMetricId",
                "lookback": {
                  "value": 1,
                  "period": "days"
                }
              }
            }
          ],
          "lastSeen": [],
          "path": "https://cottonon.com/US/everyday-3%2F4-sleeve-boat-neck-top/2004532-07.html?dwvar_2004532-07_color=2004532-07&cgid=womens-long-sleeve-tops&originalPid=2004532-07#start=1",
          "sessionId": "JS0SF1M8-304C-7511-E319-31C192EE5887",
          "v1ClientId": 20227,
          "metrics": {
            "basketItemMetricId": [],
            "productMetricId": [
              "everyday_3/4_sleeve_boat_neck_top"
            ]
          }
        }
        """
    },
    {
        "name": "TAGGSTAR_N34YG",
        "url": "https://api.taggstar.com/api/v2/key/very/product/visit",
        "body": """{
          "visitor": {
            "id": "cc9dcc21-2d5e-11e9-be9a-3f32dc7f87b2",
            "sessionId": "cc9df332-2d5e-11e9-be9a-3f32dc7f87b2"
          },
          "product": {
            "id": "N34YG",
            "name": "Superdry Hawk Coloured Faux Fur Parka - Navy",
            "price": 99,
            "category": "/Casual Coats/womens_coats_casual"
          },
          "experiment": {
            "id": "test",
            "group": "treatment"
          }
        }"""
    }
    ]
