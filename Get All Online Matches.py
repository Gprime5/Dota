from requests import get
from json import loads
from threading import Thread
from configparser import ConfigParser as cfps

config = cfps()
config.read("Texts\\info.ini")

class main(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        with open("Texts\\Hero Id.txt") as file:
            self.hero_ids = loads(file.read())

        self.matches = []

    def run(self):
        url = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1"

        for hero in list(range(1, 24)) + list(range(25, 114)):
            parameters = {
                "key" : config["Data"]["key"],
                "account_id" : config["Data"]["account_id"],
                "hero_id": str(hero)
            }
            
            print(self.hero_ids[hero], end = " ")
            
            response = get(url, parameters).json()["result"]

            self.g(response)
            
            print(response["num_results"], end = " ")

            while response["results_remaining"] > 0:
                last_match = str(response["matches"][-1]["match_id"] - 1)
                parameters["start_at_match_id"] = last_match
                response = get(url, parameters).json()["result"]

                self.g(response)
                print(response["num_results"], end = " ")
                
            print("Done")

        with open("Texts\\Online Match History.txt", "w") as file:
            matches = sorted(self.matches, key = lambda n: int(n[12:22]))
            file.write("".join(matches))

    def g(self, r):
        line_string = [',"start_time":', ',"players":[', ',"account_id":']

        match_string = '{"match_id":{0[match_id]}{1}{0[start_time]}{2}'
        player_string = '{"hero_id":{0[hero_id]:>3}{3}{0[account_id]:>10}}}'
        
        for match in r["matches"]:
            temp = match_string.format(match, *line_string)
            
            players = []
            for player in match["players"]:
                player["account_id"] = player.get("account_id") or -1
                players.append(player_string.format(player, *line_string))
            
            self.matches.append("".join(temp + ",".join(players)) + "\n")

if __name__ == "__main__":
    x = main()
    x.start()
