# Typings
from typing import List
# Packages
from .utils.request import *
from .utils.errors import *
from .group import *
from .user import *
from .traderequest import *
from .auth import *
import json as j
import asyncio
from bs4 import BeautifulSoup

class Client:
    """
    Client
    """
    def __init__(self, cookie=None, debug=False):
        """
        Created a client.
        :param cookie: A roblox cookie to login with
        """
        self.request = Request(cookie, debug)

    async def get_self(self):
        """
        Gets the user the lib is logged into.
        :return: The user
        """
        if not ".ROBLOSECURITY" in self.request.cookies:
            raise NotAuthenticated("You must be authenticated to preform that action.")
        r = await self.request.request(url="https://www.roblox.com/my/profile", method="GET")
        data = r.json()
        return User(self.request, data["UserId"], data["Username"])


    async def get_trade_info(self, TradeId) -> List[TradeRequest]:
        """
        Gets info about a trade
        :return: trade info
        """

        data = j.dumps({
            'startindex': 0,
            'statustype': 'inbound'
        })
        
        r = await self.request.request(url=f'https://trades.roblox.com/v1/trades/{TradeId}', data=data, method='GET')
        
        data = json.loads(r.content)
       
        return data

    async def get_user_by_username(self, roblox_name: str) -> User:
        """
        Gets a user using there username.
        :param roblox_name: The users username
        :return: The user
        """
        r = await self.request.request(url=f'https://api.roblox.com/users/get-by-username?username={roblox_name}', method="GET", noerror=True)
        json = r.json()
        if r.status_code != 200 or not json.get('Id') or not json.get('Username'):
            return None
        return User(self.request, json['Id'], json['Username'])

    async def get_item_sellers(self, item_id):
        """
        Gets a user using there username.
        :param roblox_name: The users username
        :return: The user
        """
        response = await self.request.request(url=f'https://economy.roblox.com/v1/assets/{item_id}/resellers?limit=25', method="GET", noerror=True)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    async def get_user_item_sell_data(self, item_id, user_id):
        
        response = await self.request.request(url=f'https://economy.roblox.com/v1/assets/{item_id}/users/{user_id}/resellable-copies', method="GET", noerror=True)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def get_user_presense(self, user_id):
        url = 'https://presence.roblox.com/v1/presence/users'
        data = j.dumps({"userIds": [user_id]})
        
        request = await self.request.request(url=url,data=data, headers = {"Content-Length":"0"}, method='POST')
        return request

    async def get_user_by_id(self, roblox_id: int) -> User:
        """
        Gets a user using there id.
        :param roblox_id: The users id
        :return: The user
        """
        r = await self.request.request(url=f'https://api.roblox.com/users/{roblox_id}', method="GET", noerror=True)
        json = r.json()
        if r.status_code != 200 or not json.get('Id') or not json.get('Username'):
            return None
        return User(self.request, json['Id'], json['Username'])

    async def get_user(self, name=None, id=None) -> User:
        """
        Does the same thing as get_user_by_username and get_user_by_id just with optional arguments
        :param name: Not required the users username
        :param id: Not required the users id
        :return: The user
        """
        if name:
            return await self.get_user_by_username(name)
        if id:
            return await self.get_user_by_id(id)
        return None

    async def get_friends(self) -> List[User]:
        """
        Gets the logged in users friends
        :return: A list of users
        """
        me = await self.get_self()
        r = await self.request.request(url=f'https://friends.roblox.com/v1/users/{me.id}/friends', method="GET")
        data = r.json()
        friends = []
        for friend in data['data']:
            friends.append(User(self.request, friend['id'], friend['name']))
        return friends

    async def change_status(self, status: str) -> int:
        """
        Changes the logged in users status
        :param status:
        :return: StatusCode
        """
        data = {'status': str(status)}
        r = await self.request.request(url='https://www.roblox.com/home/updatestatus', method='POST', data=j.dumps(data))
        return r.status_code
    async def set_item_sale_price(self, item_id, item_ua_id, price):
        
        data = {"price": price}
        r = await self.request.request(url=f'https://economy.roblox.com/v1/assets/{item_id}/resellable-copies/{item_ua_id}', method='patch', data=j.dumps(data))
        return r.status_code
    

    async def login(self, username=None, password=None, key=None):
        """
        Logs in to a roblox account with 2captcha
        :param username: The account username
        :param password: The account password
        :param key: 2captcha token
        :return: None
        """
        client = Auth(self.request)
        if not username or not password:
            raise AuthenticationError("You did not supply a username or password")
        status, cookies = await client.login(username, password)
        if status == 200 and ".ROBLOSECURITY" in cookies:
            self.request = Request(cookies[".ROBLOSECURITY"])
        if not key:
            raise CaptchaEncountered("2captcha required.")
        else:
            captcha = Captcha(self.request, key)
            data, status = await captcha.create_task()
            token = ''
            if status == 200:
                while True:
                    r, s = await captcha.check_task(data["request"])
                    if r['request'] != "CAPCHA_NOT_READY":
                        token = r['request']
                        break
                    await asyncio.sleep(1.5)
        status, cookies = await client.login(username, password, token)
        if status == 200 and ".ROBLOSECURITY" in cookies:
            self.request = Request(cookies[".ROBLOSECURITY"])

    async def get_user_items(self, user_id):
        try:
            items = []
            baseUrl = f'https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?sortOrder=Asc&limit=100'
            r = await self.request.request(url=baseUrl, method='GET', headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
            data = json.loads(r.content)
            for item in data['data']:
                items.append({'asset_id':item['assetId'], 'ua_id':item['userAssetId']})
            cursor = data['nextPageCursor']
            while cursor != None:
                r = await self.request.request(url=baseUrl + f'&cursor={cursor}', method='GET', headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
                data = json.loads(r.content)
                for item in data['data']:
                    
                    items.append({'asset_id':item['assetId'], 'ua_id':item['userAssetId']})
                cursor = data['nextPageCursor']
            return items
        except:
            return None
        
    async def send_trade(self, my_user_id, requesting_user_id, offered_items, requesting_item_id, their_user_items):
        """
        sends a trade request.
        :return: StatusCode
        """
        def get_serial(user_id, item_id):
            items = their_user_items
            for item in items:
                if item['asset_id'] == item_id:
                    return item['ua_id']

        offered_serials = []
        for item in offered_items:
            offered_serials.append(item['ua_id'])

        requesting_cerial = get_serial(requesting_user_id, requesting_item_id)
        
        url = 'https://trades.roblox.com/v1/trades/send'
        data = j.dumps({'offers':[{'userId':my_user_id, 'userAssetIds':offered_serials, 'robux':0}, {'userId':requesting_user_id, 'userAssetIds':[requesting_cerial], 'robux':0}]})
        try:
            request = await self.request.request(url=url,data=data, headers = {"Content-Length":"0"}, method='POST')
            return request.status_code
        except Exception as e:
            return e

    

                
            
       




