from json import loads
import webbrowser as w
from requests import get
from requests.exceptions import ConnectionError
from configparser import ConfigParser as cfps
from threading import Thread

config = cfps()
config.read("Texts\\info.ini")

with open("Texts\\Hero Id.txt") as file:
    hero_id = loads(file.read())

def getMatches(account_id, file_data):
    """ Find tuple list of player data in match history """
    
    result = []

    for match in file_data:
        n = [m["account_id"] for m in match["players"]]

        if account_id in n:
            index = n.index(account_id)
            hero = hero_id[match["players"][index]["hero_id"]]
            result.append((str(index), hero, str(match["match_id"])))

    return result

def getPlayerNames(ids):
    """ Get player names from dota api """

    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002"

    to_64 = lambda i: str(int(i) + 76561197960265728)
    to_32 = lambda i: int(i) - 76561197960265728
    
    parameters = {
        "key": config["Data"]["key"],
        "steamids": ",".join(to_64(i) for i in ids)
    }

    try:
        response = get(url, parameters)
    except ConnectionError:
        return

    if "[Canât connect to Broadband]" in response.text:
        return
    
    player_data = response.json()["response"]["players"]
    players = [(to_32(i["steamid"]), i["personaname"]) for i in player_data]

    return sorted(players, key = lambda x: x[1])

def getServerIds():
    file_path = "\\".join(["C:\\Program Files (x86)\\Steam\\steamapps\\common",
                           "dota 2 beta\\game\\dota\\server_log.txt"])

    with open(file_path) as file:
        for line in file.readlines()[::-1]:
            start = line.find("(Lobby")
            if start > -1:
                end = line.find(")", start)
                values = line[start:end].split(" ")[3:]
                values = [i[i.find(":[U:1:") + 6:-1] for i in values]
                values.remove(config["Data"]["account_id"])
                
                return values

def getPros():
    with open("Texts\\Pros.txt", "rb") as file:
        lines = file.read().decode().splitlines()[1:]

    return dict([n.split(" ", 1) for n in lines])

class load():
    def __init__(self, tk = None):
        self.tk = tk

    def log(self, txt):
        if self.tk:
            self.tk.lbl.configure(text = txt)

    def insert(self, txt, v, t, tv_id = ""):
        return self.tk.tv.insert(tv_id, "end", text = txt, values = v, tags = t)

    def run(self):
        Thread(target=self._run).start()

    def _run(self):
        self.log("Loading players")
        self.tk.tv.tag_configure('pro', foreground="white", background='black')

        with open("Texts\\Match History.txt") as file:
            file_data = [loads(i) for i in file.readlines()][::-1]

        players = getPlayerNames(getServerIds())
        pros = getPros()

        if players is None:
            self.log("No connection")
            return
        
        for tv_id in self.tk.tv.get_children():
            self.tk.tv.delete(tv_id)
            
        for account_id, name in players:
            matches = getMatches(account_id, file_data)
            tags = ["player"]

            if account_id in pros:
                name = "{} ({})".format(name, pros[account_id])
                tags.append("pro")

            tv_id = self.insert(name, str(len(matches)), tags)
            
            for slot, hero, match_id in matches:
                self.insert(slot + " " + hero, match_id, "match", tv_id)
                
        self.log("Loaded")

if __name__ == "__main__":
    with open("Texts\\Match History.txt") as file:
        file_data = [loads(i) for i in file.readlines()][::-1]
        
    m = getMatches(int(input("ID: ")), file_data)
    
    if m:
        name_len = len(max(m, key = lambda x: len(x[1]))[1])
        text = "{1} {2: <{0}} https://www.dotabuff.com/matches/{3}"
        for i in m:
            print(text.format(name_len, *i))
