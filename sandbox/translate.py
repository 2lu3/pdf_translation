import requests
import os

API_KEY = os.environ.get("DEEPL_API_KEY")

text = "Riemann Zeta function is a very important function in number theory."
source_lang = 'EN'
target_lang = 'JA'

# パラメータの指定
params = {
            'auth_key' : API_KEY,
            'text' : text,
            'source_lang' : source_lang, # 翻訳対象の言語
            "target_lang": target_lang  # 翻訳後の言語
        }

# リクエストを投げる
request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
result = request.json()

print(result)
