from fastapi import FastAPI
from db import make_db
import pickle
import sqlite3
import random

app = FastAPI()
make_db()

db = sqlite3.connect("novaex.db")
c = db.cursor()

@app.get("/points/{user_id}")
async def get_points(user_id: int) -> int:
    """
        :param user_id: The ID of the user to get points for.
        :return: int: The number of current points (not counting points in websites)
    """
    return c.execute("SELECT points FROM users WHERE id=?", (user_id,)).fetchone()[0]

@app.get("/website/random")
async def get_random_website() -> str:
    """
        :return: str: The random URL to visit
    """
    ids = c.execute("SELECT id FROM users").fetchall()
    min = 1
    max = 1
    counter = 0
    for i in ids:
        n = ids[counter]
        if n > max:
            max = n
        if n < min:
            min = n
        counter += 1
    random_id = random.randint(min, max)
    sites = c.execute("SELECT sites FROM users WHERE id=?", (random_id,)).fetchone()[0]
    sites_dict = pickle.loads(sites)
    max = [0, "url"]
    for url in sites_dict:
        if sites_dict[url]["points"] > max[0] and sites_dict[url]["points"] >= sites_dict[url]["price"]:
            max = [sites_dict[url]["points"], url]
    if max[0] == 0 or sites_dict[max[1]]["points"] < sites_dict[max[1]]["price"]:
        pass
        # TODO: retry get url
    else:
        return max[1]

@app.post("/add/{user_id}/{points}")
async def add_point(user_id: int, points: int) -> bool:
    """
        :param user_id: The ID of the user to add points for.
        :param points: The number of points to add to the user.
        :return: bool: True if succesfully added, False if database error occurs or user not found.
    """
    # TODO: authentication for "system user"
    r = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()[0]
    if r == None:
        return False
    try:
        cur_points = c.execute("SELECT points FROM users WHERE id=?", (user_id,)).fetchone()[0]
        c.execute("UPDATE users SET points=?", (cur_points + points,))
        db.commit()
        return True
    except:
        return False
        
@app.post("/add-website/{user_id}/{url}")
async def add_website(user_id: int, url: str):
    """
        :param user_id: The user to add the website to.
        :return: bool: True if succesfully added, False if database error occurs or user not found.
    """
    # TODO: authentication for TBD in project planning
    r = c.execute("SELECT sites FROM users where id = ?", (user_id,)).fetchone()[0]
    if r == None:
        return False
    try:
        if r == "no websites":
            sites = pickle.dumps({url: {"points": 0, "cost": 0}})
            c.execute("UPDATE users SET sites = ? WHERE id=?", (sites, user_id))
            db.commit()
            return True
        else:
            sites_dict = pickle.loads(r)
            sites_dict[url] = {"points": 0, "cost": 0}
            sites = pickle.dumps(sites_dict)
            c.execute("UPDATE users SET sites = ? WHERE id=?", (sites, user_id))
            db.commit()
            return True
    except:
        return False    