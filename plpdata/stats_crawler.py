import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
import json

def get_season(play_time: datetime) -> str:
    current_year = play_time.year

    if play_time > datetime(current_year, 10, 1):
        season = f"{current_year}-{current_year+1}"
    else:
        season = f"{current_year-1}-{current_year}"
    return season


def get_game_info(game_id: int) -> dict:
    """
    game_type, game_number, location, home, away, 
    """
    url = f"https://pleagueofficial.com/game/{game_id}"
    
    logger.info(f"Retrieving data from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    basic_info = soup.find("title").getText().split(" ")
    # print(basic_info) # away | home

    logger.info(f"Extracting game info...")
    if len(basic_info) == 5: 
        game_type = basic_info[0].split('G')[0]
        game_number = basic_info[0].split('G')[1]
        home = basic_info[1]
        away = basic_info[3].split('│')[0]
    else:
        game_type = basic_info[0]
        game_number = basic_info[1]
        home = basic_info[2]
        away = basic_info[4].split('│')[0]

    # print(game_type, game_number, away, home)

    time_and_place = soup.find("span", class_="fs14").getText().split(" ")
    play_time = datetime.strptime(' '.join(time_and_place[1:3]), '%Y-%m-%d %H:%M')
    season = get_season(play_time)
    location = time_and_place[-1]

    return dict(game_id=game_id, season=season, game_type=game_type, game_number=game_number, 
                location=location, home=home, away=away, play_time=play_time)


def headers() -> dict:
    return {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
        # "referer": 'https://pleagueofficial.com/game/73',
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

def get_game_stats(game_id: int, game_info: dict) -> pd.DataFrame:
    url = f"https://pleagueofficial.com/api/boxscore.php?id={game_id}&away_tab=total&home_tab=total"

    res = requests.get(
        url, headers=headers()
    )
    logger.info(f"Extract game stats from '{url}'")

    if res.json()['data']['home']: 
        df_home = pd.DataFrame(res.json()['data']['home'])
        df_away = pd.DataFrame(res.json()['data']['away'])
        df_home['team_name'] = game_info['home']
        df_home['is_home'] = True
        df_away['team_name'] = game_info['away']
        df_away['is_home'] = False
        
        df = pd.concat([df_home, df_away])
        df['game_id'] = game_id
        df['season'] = game_info['season']
        df['game_type'] = game_info['game_type']
        df['game_number'] = game_info['game_number'] 
        df['location'] = game_info['location']
        df['play_time'] = game_info['play_time']
        df['starter'] = df['starter'] == '〇'
    else: 
        logger.warning('This game has not happened yet!')
        df = pd.DataFrame()

    return df 

def main():
    logger.info("Crawling game info")

    games = []
    # for i in range(110, 111):
    i = 65
    game_info = get_game_info(i)
    df = get_game_stats(i, game_info)

        # print(game_info)

    print(pd.DataFrame([game_info]))
    print(df.head())
    # df.to_csv('game_stats.csv', index=False, encoding="utf_8_sig")
    # logger.info(f"Saved as 'game_stats.csv' ")
    # df = pd.DataFrame(games).sort_values('play_time')
    


if __name__ == '__main__':
    main()





teams = {
    "福爾摩沙台新夢想家": "Formosa Taishin Dreamers",
    "臺北富邦勇士": "Taipei Fubon Braves",
    "高雄鋼鐵人": "Kaohsiung Steelers",
    "桃園領航猿": "Taoyuan Pilots",
    "新北國王": "New Taipei Kings",
    "新竹街口攻城獅": "Hsinchu Jko Lioneers"
}