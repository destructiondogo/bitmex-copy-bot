TESTNET_URL = "https://testnet.bitmex.com/api/v1/"
MAINNET_URL = "https://www.bitmex.com/api/v1/"

LEADERS = {
    'LEADER_A' : {

        'API_KEY' : 'GJC80Kr4BwnghuulKl6VprTH',
        'API_SECRET' : 'POWn13jhwNO0N8Wg1GA0BnvybM_r8Jwbaa52igRGgaiZOk7B',
        'ENDPOINT' : TESTNET_URL

    },
    'LEADER_B' : {

        'API_KEY' : 'dsdBfhkqpQ6imYGbXhZTqyUt',
        'API_SECRET' : 'JaT8I0zlSIrH4uXCTYBnhQNBZitVkccyt14MODImrO1MhvS2',
        'ENDPOINT': TESTNET_URL

    }

}

FOLLOWERS = {
    'FOLLOWER_A' : {

        'API_KEY': 'NwXfK-nQhrbQ8vDJOb8T-B4_',
        'API_SECRET': 'fRIyyzTdns_ZQIk-LSk2XHl7ncv_aZ5fD2hUt7CNs2_kHy5d',
        'ENDPOINT': TESTNET_URL,
        'FOLLOWS' : {
            'LEADER_A' : '30%',
            'LEADER_B' : '20%'
        }

    },
    'FOLLOWER_B' : {

        'API_KEY': 'jfGfGY_tj8THivDzl7Xd3BJp',
        'API_SECRET': 'En8htoBGqeiCgOY5d-inj6_vvgDJodwcj5WxBwpKffGjHd_E',
        'ENDPOINT': TESTNET_URL,
        'FOLLOWS' : {
            'LEADER_B' : '110%'
        }

    }
}