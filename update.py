from pyautogui import click as c, FailSafeException, typewrite, position, moveTo
from PIL.ImageGrab import grab
from PIL import Image
from time import sleep, time
from requests import get
from configparser import ConfigParser as cfps
from requests.exceptions import ConnectionError
from threading import Thread

config = cfps()
config.read("Texts\\info.ini")

# List of (bounding box, image name)
image_data = (
    ((767, 180, 832, 188), "duration"),
    ((86, 181, 135, 195), "score"),
    ((1225, 197, 1290, 206), "friend_id"),
    ((1310, 65, 1365, 80), "search_match_id"),
    ((570, 79, 624, 90), "audio")
)

get_image_bytes = lambda img: Image.open("Images\\" + img + ".png").tobytes()

images = {img: (bbox, get_image_bytes(img)) for bbox, img in image_data}

def click(x, y):
    """

    Click the screen at position x, y

    x = horizontal position
    y = vertical position
    
    """
    
    try:
        c(x, y)
    except PermissionError:
        pass

def wait(img_name, timeout = 5, threshold = 30):
    """

    Blocks until image is shown at location or timeout
    
    timeout raises pyautogui.exception.FailSafeException
    move mouse to position (0, 0) to apply FailSafeException at any time

    img = image bytes object
    threshold = acceptable difference in image data

    """
    
    start = time()
    bbox, img = images[img_name]

    # Compare screenshot and the image
    zipped = zip(grab(bbox).tobytes(), img)
    difference = sum(abs(scrn - img) for scrn, img in zipped)

    while difference > threshold:
        sleep(.1)

        if position() == (0, 0):
            raise FailSafeException

        if time() - start > timeout:
            raise FailSafeException

        zipped = zip(grab(bbox).tobytes(), img)
        difference = sum(abs(scrn - img) for scrn, img in zipped)

    return True

def scan_account_id():
    """ Scan screenshot area (1290, 197, 1380, 206) for an account id """

    screen = grab((1290, 197, 1380, 206)).tobytes().hex()

    # Vertical unique slice of number image to match
    numbers = [
        '000000000000474747878787999999929292787878000000000000',
        '000000b0b0b0939393000000000000000000000000000000000000',
        '0000005555553f3f3f000000000000000000000000000000828282',
        '0000002f2f2f000000000000000000000000000000000000262626',
        '000000000000000000000000000000919191939393000000000000',
        '0000000000000000000000000000000000000000004d4d4d676767',
        '0000000000000000000000007d7d7da0a0a0a3a3a3757575000000',
        '717171808080000000000000000000000000000000000000474747',
        '0000000000005b5b5b0000000000003f3f3f909090737373000000',
        '0000003535359a9a9aa4a4a46d6d6d000000000000000000000000'
    ]

    # Function to split a list into evenly sized chunks
    chunk = lambda lst, n: [lst[i:i + n] for i in range(0, len(lst), n)]

    # rows of columns = screen_slices[row][column]
    rows_of_columns = [chunk(row, 6) for row in chunk(screen, 540)]

    # Transpose to vertical slices = screen_slices[column][row]
    screen_slices = ["".join(b) for b in zip(*rows_of_columns)]

    account_id = []

    while set(screen_slices) & set(numbers):
        # Get first match
        num = (set(screen_slices) & set(numbers)).pop()

        # Get horizontal position of match in screen_slice
        slice_index = screen_slices.index(num)

        account_id.append((slice_index, str(numbers.index(num))))

        # Change screen_slices to avoid duplicates
        screen_slices[slice_index] = 0

    # Return account id sorted by slice_index
    account_id = sorted(account_id, key = lambda k: k[0])
    
    return "".join(data[1] for data in account_id)

def newMatches():
    url = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1"

    try:
        response = get(url, config["Data"])
    except ConnectionError:
        return

    if "[Canât connect to Broadband]" in response.text:
        return
    
    with open("Texts\\Match History.txt") as file:
        saved_matches = [int(n[12:22]) for n in file.readlines()]

    r = response.json()

    if r.get("result"):
        return [n for n in r["result"]["matches"]
                if n["match_id"] not in saved_matches][::-1]
    
def beginSequence():
    click(66, 25)
    wait("audio")
    click(579, 84)
    moveTo(190, 190)
    click(190, 190)
    sleep(.1)
    click(664, 25)
    sleep(.1)
    click(664, 25)
    click(664, 25)
    sleep(.3)
    click(777, 72)

def endSequence():
    click(66, 25)
    wait("audio")
    click(579, 84)
    moveTo(466, 190)
    click(466, 190)
    sleep(.1)
    click(244, 30)
    sleep(.1)
    click(244, 30)

def replayScreenSequence(match_id):
    wait("search_match_id")
    click(1316, 67) # Click on search input
    typewrite(str(match_id))
    click(1513, 73) # Click search icon

def scoreboardScreenSequence():
    y_values = (220, 270, 320, 370, 420, 520, 570, 620, 670, 720)
    ids = []

    wait("duration")
    click(416, 130) # Click to scoreboard
    sleep(.4)
    
    for index, data in enumerate(y_values):
        sleep(.4)
        wait("score")
        click(115, data) # Click to profile
        sleep(.4)
        scan = scan_account_id()
        while not scan:
            click(115, data) # Click to profile
            sleep(.1)
            scan = scan_account_id()
        ids.append(scan)
        click(113, 25) # Return
    click(113, 25) # Return

    return ids

def save(match, ids):
    match_string = '{{"match_id":{0[match_id]},"start_time":{0[start_time]},"players":['
    player_string = '{{"hero_id":{0[hero_id]:>3},"account_id":{1:>9}}},'

    string = [match_string.format(match)]
    
    for player, account_id in zip(match["players"], ids):
        string.append(player_string.format(player, account_id))

    with open("Texts\\Match History.txt", "a") as file:
        file.write("".join(string)[:-1] + "]}\n")

class update():
    """ Main update process """
    def __init__(self, lbl = None):        
        self.lbl = lbl

    def log(self, txt):
        if self.lbl:
            self.lbl.configure(text = txt)

    def run(self):
        Thread(target=self._run).start()

    def _run(self):
        new = newMatches()

        if new:
            self.log("Updating players")
        
            try:
                beginSequence()
                
                for match in new:
                    replayScreenSequence(match["match_id"])

                    if match["lobby_type"] in (0, 7):
                        save(match, scoreboardScreenSequence())

                    click(113, 25) # Return

                endSequence()
                self.log("Updated")
            except FailSafeException:
                self.log("Failsafe executed")
        elif new == []:
            self.log("No matches to update")
        else:
            self.log("No connection")
