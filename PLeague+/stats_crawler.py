import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger

def get_season(play_time) -> str:
    current_year = play_time.year

    if play_time > datetime(current_year, 10, 1):
        season = f"{current_year}-{current_year+1}"
    else:
        season = f"{current_year-1}-{current_year}"
    return season


def get_game_info(game_id) -> dict:
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
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
        "cookie": "PHPSESSID=6qbctjqkjpcq6akosbsnosc7f9; _ga=GA1.1.2039077758.1649901582; _ga_E4T1HDWQ3D=GS1.1.1650807763.5.1.1650808386.58",
        # "referer": "https://pleagueofficial.com/game/151",
        "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"''',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "'Android'",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Mobile Safari/537.36",
        "x-requested-with": "XMLHttpRequest",    
    }

def get_game_stats(game_id, game_info) -> pd.DataFrame:
    url = f"https://pleagueofficial.com/api/boxscore.php?id={game_id}&away_tab=total&home_tab=total"

    res = requests.get(
        url, headers=headers()
    )
    logger.info(f"Extract game stats from '{url}'")

    # print(res.json()['data'])

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

    return df 

def main():
    logger.info("Crawler first 10 game info")

    games = []
    for i in range(110, 111):
        # games.append(get_game_info(i))
        game_info = get_game_info(i)
        df = get_game_stats(i, game_info)

        # print(game_info)

    # print(df)
    df.to_csv('game_stats.csv', index=False, encoding="utf_8_sig")
    # df = pd.DataFrame(games).sort_values('play_time')
    


if __name__ == '__main__':
    main()