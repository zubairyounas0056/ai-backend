from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables, get_db
# from task_engine import run_parallel, stop_all_tasks
# from scheduler import add_interval_job
# from ai_engine import process_input
# from control import STOP_FLAG, start_listener
# from ai_brain import think
# from vpn_manager import add_vpn, load_vpns, remove_vpn
from concurrent.futures import ThreadPoolExecutor

# import subprocess
import os
import requests
import datetime
# import time
import urllib.parse
# import websocket
import json
import random
# import threading

# 🔥 ACTIVE BROWSERS TRACKING
active_browsers = {}

# ================= USER DATABASE =================

users_db = {
    "admin@gmail.com": {"status": "active"},
    "test@gmail.com": {"status": "active"},
    "blocked@gmail.com": {"status": "disabled"},
}


def get_user_from_db(email):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        return users.get(email)
    except:
        return None


# ================= UNIVERSAL COMMENT JS =================
def get_comment_js(comment):

    js = """
    (function(){

        function sleep(ms){
            return new Promise(r => setTimeout(r, ms));
        }

        async function run(){

            // 🔥 SCROLL FORCE
            window.scrollBy(0, 500);
            await sleep(300);

            function findInput(){

                // 🥇 UNIVERSAL
                let elements = document.querySelectorAll("textarea, input, div");

                for(let el of elements){
                    let rect = el.getBoundingClientRect();

                    if(
                        el.isContentEditable ||
                        el.tagName === "TEXTAREA" ||
                        el.getAttribute("role") === "textbox"
                    ){
                        if(rect.width > 200 && rect.height > 20){
                            return el;
                        }
                    }
                }

                // 🥈 TikTok specific fallback
                let tiktok = document.querySelector('[contenteditable="true"]');
                if(tiktok) return tiktok;

                return null;
            }

            let input = null;

            for(let i=0;i<6;i++){
                input = findInput();
                if(input) break;

                window.scrollBy(0, 200);
                await sleep(300);
            }

            if(!input){
                return "NOT_FOUND";
            }

            // 🔥 FORCE CLICK
            input.focus();
            input.click();
            await sleep(200);

            // 🔥 TYPE
            if(input.value !== undefined){
                input.value = "__COMMENT__";
            }else{
                input.innerText = "__COMMENT__";
            }

            let event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);

            await sleep(200);

            // 🔥 ENTER SPAM
            for(let i=0;i<3;i++){
                let e = new KeyboardEvent("keydown", {
                    bubbles: true,
                    cancelable: true,
                    keyCode: 13
                });
                input.dispatchEvent(e);
                await sleep(100);
            }

            return "DONE";
        }

        return run();

    })();
    """

    return js.replace("__COMMENT__", comment)


app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DB =================
create_tables()


# ================= DEFAULT ADMIN =================
def seed_admin():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", ("admin@gmail.com",))
    admin = cursor.fetchone()

    if not admin:
        cursor.execute(
            "INSERT INTO users (email, password, role, status) VALUES (?, ?, ?, ?)",
            ("admin@gmail.com", "1234", "admin", "active"),
        )
        conn.commit()

    conn.close()


seed_admin()


def monitor_browsers():
    while True:
        to_remove = []

        for id, port in active_browsers.items():
            try:
                requests.get(f"http://127.0.0.1:{port}/json", timeout=0.2)
            except:
                to_remove.append(id)

        for id in to_remove:
            del active_browsers[id]

        time.sleep(2)


# threading.Thread(target=monitor_browsers, daemon=True).start()


# ================= TARGET PARSER =================
def parse_targets(target_str):

    if not target_str or str(target_str).strip() == "":
        return [1]  # default browser

    target_str = str(target_str)

    if "-" in target_str:
        start, end = map(int, target_str.split("-"))
        return list(range(start, end + 1))

    if "," in target_str:
        return [int(x.strip()) for x in target_str.split(",")]

    return [int(target_str)]


# ================= SMART TASK PARSER =================
def parse_smart_chain(input_str):

    steps = input_str.split("->")
    tasks = []

    for step in steps:
        step = step.strip()

        parts = step.split()

        if len(parts) < 2:
            continue

        targets = parse_targets(parts[0])
        url = parts[1]

        # auto add https
        if not url.startswith("http"):
            url = "https://" + url

        tasks.append(
            {
                "type": "open_url",
                "data": {"targets": targets, "url": url, "new_tab": False},
            }
        )

    return tasks


# ================= SMART DELAY =================
def smart_delay(min_sec=2, max_sec=5):

    delay = random.randint(min_sec, max_sec)
    print(f"⏳ WAITING {delay} sec...")
    time.sleep(delay)


# ================= SIGNUP =================
@app.post("/signup")
def signup(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    email = data.get("email")
    password = data.get("password")

    # check exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return {"status": "exists"}

    # 🔥 CORRECT INSERT
    cursor.execute(
        "INSERT INTO users (email, password, role, status, expiry) VALUES (?, ?, ?, ?, ?)",
        (email, password, "user", "active", None),
    )

    conn.commit()
    conn.close()

    return {"status": "success"}


# ================= LOGIN =================
@app.post("/login")
def login(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data.get("email"), data.get("password")),
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"status": "error"}

    # ❌ Disabled check
    if user["status"] != "active":
        conn.close()
        return {"status": "blocked"}

    # 🔥 expiry check
    if "expiry" in user.keys() and user["expiry"]:
        expiry_date = datetime.datetime.strptime(user["expiry"], "%Y-%m-%d")
        if datetime.datetime.now() > expiry_date:
            conn.close()
            return {"status": "expired"}

    # ✅ log
    cursor.execute(
        "INSERT INTO logs (email, ip, login_time) VALUES (?, ?, ?)",
        (data.get("email"), "127.0.0.1", str(datetime.datetime.now())),
    )
    conn.commit()

    conn.close()

    return {
        "status": "success",
        "role": user["role"],
        "email": user["email"],
        "expiry": user["expiry"],  # 🔥 ADD THIS
    }


# ================= USERS =================
@app.get("/users")
def get_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return [dict(user) for user in users]


@app.post("/toggle-user")
def toggle_user(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    user_id = data.get("id")

    cursor.execute("SELECT status FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"status": "error"}

    cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
    role_data = cursor.fetchone()
    
    if role_data["role"] == "admin":
        conn.close()
        return {"status": "blocked"}  # ❌ admin disable not allowed
    
    new_status = "disabled" if user["status"] == "active" else "active"

    cursor.execute("UPDATE users SET status=? WHERE id=?", (new_status, user_id))

    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.post("/delete-user")
def delete_user(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    user_id = data.get("id")

    # ❌ Admin delete block
    cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"status": "error"}

    if user["role"] == "admin":
        conn.close()
        return {"status": "blocked"}  # admin delete allowed nahi

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

    return {"status": "deleted"}


# ================= LOGS =================
@app.get("/logs")
def get_logs():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()

    conn.close()

    return [dict(log) for log in logs]


# ================= TASKS =================
@app.get("/tasks")
def get_tasks(user_email: str = ""):

    conn = get_db()
    cursor = conn.cursor()

    if user_email:
        cursor.execute("SELECT * FROM tasks WHERE data LIKE ?", (f"%{user_email}%",))
    else:
        cursor.execute("SELECT * FROM tasks")

    tasks = cursor.fetchall()

    conn.close()
    return [dict(task) for task in tasks]


@app.post("/add-task")
def add_task(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (name, type, data, status) VALUES (?, ?, ?, ?)",
        (
            data.get("name"),
            data.get("type", "open_browser"),
            json.dumps(data.get("data", {})),
            "stopped",
        ),
    )

    conn.commit()
    conn.close()
    return {"status": "added"}


@app.post("/toggle-task")
def toggle_task(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    task_id = data.get("id")

    cursor.execute("SELECT status FROM tasks WHERE id=?", (task_id,))
    task = cursor.fetchone()

    if not task:
        conn.close()
        return {"status": "error"}

    new_status = "stopped" if task["status"] == "running" else "running"

    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))

    conn.commit()
    conn.close()
    return {"status": "updated"}


# ================= OPEN URL (SMART RETRY) =================
@app.post("/open-url")
def open_url(data: dict):
    return {"status": "disabled_on_server"}

    targets = data.get("targets", [])
    url = data.get("url")
    use_new_tab = data.get("new_tab", False)

    print("🔥 OPEN_URL CALLED", targets, url, "new_tab:", use_new_tab)

    if not targets or not url:
        return {"status": "error"}

    results = []

    for i in targets:

        port = 9221 + i
        success = False

        print(f"➡️ Profile {i} | Port {port}")

        # 🔁 RETRY LOOP
        for attempt in range(3):
            try:
                print(f"🔁 Attempt {attempt + 1}")

                res = requests.get(f"http://127.0.0.1:{port}/json")
                tabs = res.json()

                ws_url = None

                if not use_new_tab:
                    for tab in tabs:
                        if tab.get("type") == "page":
                            ws_url = tab.get("webSocketDebuggerUrl")
                            print("🌐 USING CURRENT TAB")
                            break
                else:
                    new_tab = requests.put(f"http://127.0.0.1:{port}/json/new")
                    tab_data = new_tab.json()
                    ws_url = tab_data.get("webSocketDebuggerUrl")
                    print("🆕 USING NEW TAB")

                if not ws_url:
                    raise Exception("No websocket URL")

                ws = websocket.create_connection(ws_url)

                ws.send(
                    json.dumps(
                        {"id": 1, "method": "Page.navigate", "params": {"url": url}}
                    )
                )

                result = ws.recv()
                print(f"🧠 RESULT {i}: {result}")

                ws.close()

                print("✅ SUCCESS")

                results.append(f"profile {i} opened")
                success = True
                break

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")

                if attempt < 2:
                    print("🔁 RETRYING...")
                    time.sleep(2)
                else:
                    print("🚫 FINAL FAIL")

        if not success:
            results.append(f"profile {i} failed")

    return {"status": "done", "details": results}


# ================= RUN TASK =================
@app.post("/run-task")
def run_task(data: dict):
    return {"status": "disabled_on_server"}

    task_id = data.get("id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = cursor.fetchone()

    conn.close()

    if not task:
        return {"status": "error"}

    task_type = task["type"]
    print("🧠 TASK TYPE:", task_type)

    try:
        task_data = json.loads(task["data"])
        print("🧠 TASK DATA:", task_data)
    except:
        task_data = {}

    input_str = task_data.get("input")
    ai_actions = []

    if input_str:
        ai_actions = think(input_str)
    mode = task_data.get("mode", "ai")

    # ================= SMART CHAIN =================
    if input_str and "->" in input_str:
        print("🧠 SMART CHAIN DETECTED")

        chain_tasks = parse_smart_chain(input_str)
        run_task_chain(chain_tasks)

        return {"status": "running"}

    # ================= OPEN BROWSER =================
    if task_type == "open_browser":

        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, "tools", "launcher_api.js")

        subprocess.Popen(["node", script_path, str(task_data.get("input"))])

        # 🔥 TRACK BROWSERS
        targets = parse_targets(task_data.get("input"))

        for t in targets:
            port = 9221 + t
            active_browsers[t] = port

    # ================= OPEN URL =================
    elif task_type.strip().lower() == "open_url":

        print("🚀 ENTERED open_url BLOCK")

        input_str = task_data.get("input")

        # 🤖 AI ENGINE
        ai_result = process_input(input_str, mode)

        print("🤖 AI RESULT:", ai_result)

        input_str = ai_result["final_input"]
        global_delay = ai_result["delay"]

        # ================= CASE 1 =================
        if "start" in task_data and "end" in task_data and "url" in task_data:

            start = int(task_data["start"])
            end = int(task_data["end"])
            url = task_data["url"]

            targets = list(range(start, end + 1))
            new_tab = task_data.get("new_tab", False)

            for target in targets:
                time.sleep(global_delay)

                print(f"🌐 Opening target {target}")

                response = open_url(
                    {"targets": [target], "url": url, "new_tab": new_tab}
                )

                print("✅ RESPONSE:", response)

        # ================= CASE 2 (FIXED) =================
        else:

            if not input_str:
                return {"status": "error", "message": "No input provided"}

            input_str = input_str.strip()

            try:
                parts = input_str.split()

                if len(parts) < 2:
                    return {"status": "error", "message": "Invalid format"}

                targets = parse_targets(parts[0])
                url = parts[1]

                new_tab = False
                if len(parts) > 2 and parts[2].lower() == "new":
                    new_tab = True

            except Exception as e:
                print("❌ INPUT ERROR:", str(e))
                return {"status": "error", "message": "invalid input"}

            # 🤖 AI MODE CONTROL (FIXED)
            if mode.lower() == "ai":

                for target in targets:

                    if STOP_FLAG:
                        print("🛑 TASK STOPPED")
                        return {"status": "stopped"}

                    print(f"🌐 [AI] Opening target {target}")

                    response = open_url(
                        {
                            "targets": [target],
                            "url": url,
                            "new_tab": new_tab,
                        }
                    )

                    print("✅ RESPONSE:", response)

                    time.sleep(global_delay)

            # ⚡ INSTANT MODE (UNCHANGED)
            else:

                for target in targets:

                    if STOP_FLAG:
                        print("🛑 TASK STOPPED")
                        return {"status": "stopped"}

                    time.sleep(global_delay)

                    print(f"🌐 [INSTANT] Opening target {target}")

                    response = open_url(
                        {
                            "targets": [target],
                            "url": url,
                            "new_tab": new_tab,
                        }
                    )

                    print("✅ RESPONSE:", response)

    # 🔥 VPN ADD
    elif task_type == "add_vpn":
        vpn_id = task_data.get("vpn_id")
        name = task_data.get("name")
        logo = task_data.get("logo")

        result = add_vpn(vpn_id, name, logo)
        return result

    # 🔥 VPN REMOVE
    elif task_type == "remove_vpn":
        vpn_id = task_data.get("vpn_id")

        result = remove_vpn(vpn_id)
        return result

    # 🔥 VPN CONNECT  👈 👈 👈 YAHAN ADD KARNA HAI
    elif task_type == "vpn_connect":

        targets = parse_targets(task_data.get("targets"))
        vpns = load_vpns()

        print("🔥 ADVANCED VPN CONNECT START")

        import threading

        def connect_on_target(target):
            port = 9221 + target

            try:
                res = requests.get(f"http://127.0.0.1:{port}/json")
                tabs = res.json()

                ws_url = None
                for tab in tabs:
                    if tab.get("type") == "page":
                        ws_url = tab.get("webSocketDebuggerUrl")
                        break

                if not ws_url:
                    return

                ws = websocket.create_connection(ws_url)

                for vpn in vpns:
                    try:
                        print(f"🚀 TRY {vpn['name']} → Browser {target}")

                        # ---------- STEP 1: popup try ----------
                        ext_popup = f"chrome-extension://{vpn['id']}/popup.html"

                        ws.send(
                            json.dumps(
                                {
                                    "id": 1,
                                    "method": "Page.navigate",
                                    "params": {"url": ext_popup},
                                }
                            )
                        )

                        time.sleep(2)

                        # ---------- STEP 2: fallback root ----------
                        ws.send(
                            json.dumps(
                                {
                                    "id": 2,
                                    "method": "Runtime.evaluate",
                                    "params": {
                                        "expression": """
                                if(document.body.innerText.includes("ERR_FILE_NOT_FOUND")){
                                    window.location.href = window.location.origin;
                                }
                                """
                                    },
                                }
                            )
                        )

                        time.sleep(2)

                        # ---------- STEP 3: ADVANCED CLICK ----------
                        ws.send(
                            json.dumps(
                                {
                                    "id": 3,
                                    "method": "Runtime.evaluate",
                                    "params": {
                                        "expression": """
                                function tryClick(){
                                    let selectors = [
                                        "button",
                                        "[class*=connect]",
                                        "[id*=connect]",
                                        "[aria-label*=connect]",
                                        "[class*=start]",
                                        "[id*=start]",
                                        "[class*=go]",
                                        "[class*=power]",
                                        "[class*=enable]"
                                    ];

                                    for(let sel of selectors){
                                        let btn = document.querySelector(sel);
                                        if(btn){
                                            btn.click();
                                            return "CLICKED: " + sel;
                                        }
                                    }

                                    // 🔥 try all buttons
                                    let allBtns = document.querySelectorAll("button");
                                    for(let b of allBtns){
                                        if(b.innerText.toLowerCase().includes("connect") ||
                                        b.innerText.toLowerCase().includes("start") ||
                                        b.innerText.toLowerCase().includes("go")){
                                            b.click();
                                            return "CLICKED TEXT BUTTON";
                                        }
                                    }

                                    return "NO BUTTON";
                                }

                                tryClick();
                                """
                                    },
                                }
                            )
                        )

                        # ---------- STEP 4: WAIT ----------
                        time.sleep(3)

                    except Exception as e:
                        print(f"❌ FAIL {vpn['name']} → {target}")

                ws.close()

            except Exception as e:
                print("❌ Browser error:", str(e))

        threads = []

        for target in targets:
            t = threading.Thread(target=connect_on_target, args=(target,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return {"status": "done"}

        # ================= UNIVERSAL COMMENT SYSTEM =================
    elif task_type == "tiktok_comment":

        targets = parse_targets(task_data.get("targets"))
        count = int(task_data.get("count", 1))
        delay = float(task_data.get("delay", 0.3))
        mode = task_data.get("mode")
        text = task_data.get("text")

        comments_pool = [
            "Nice 🔥",
            "Amazing 😍",
            "Wow 🔥",
            "Love this ❤️",
            "Great live 👏",
            "So cool 😎",
            "🔥🔥🔥",
            "Legend 🔥",
            "Respect 💯",
            "Keep going 💪",
            "Top 🔥",
            "Best stream 😍",
            "زبردست 🔥",
            "کمال 😍",
            "واہ 👏",
        ]

        print("🚀 UNIVERSAL COMMENT ENGINE START")

        # 🔥 SEQUENTIAL LOOP (LOW LOAD)
        for target in targets:

            port = 9221 + target

            try:
                res = requests.get(f"http://127.0.0.1:{port}/json")
                tabs = res.json()

                ws_url = None
                for tab in tabs:
                    if tab.get("type") == "page":
                        ws_url = tab.get("webSocketDebuggerUrl")
                        break

                if not ws_url:
                    print(f"❌ No WS for {target}")
                    continue

                ws = websocket.create_connection(ws_url)

                for i in range(count):

                    comment = (
                        text
                        if (mode == "custom" and text)
                        else random.choice(comments_pool)
                    )

                    js_code = get_comment_js(comment)

                    ws.send(
                        json.dumps(
                            {
                                "id": 1,
                                "method": "Runtime.evaluate",
                                "params": {"expression": js_code},
                            }
                        )
                    )

                    print(f"💬 {comment} → Browser {target}")

                    time.sleep(delay)

                ws.close()

            except Exception as e:
                print(f"❌ Error on {target}:", str(e))

        return {"status": "done"}


# ================= TASK CHAIN =================
def run_task_chain(tasks):

    print("🔗 RUNNING TASK CHAIN")

    for i, task in enumerate(tasks):

        if task.get("type") == "open_url":
            open_url(task.get("data"))

        elif task.get("type") == "open_browser":

            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, "tools", "launcher_api.js")

            subprocess.Popen(
                ["node", script_path, str(task.get("data", {}).get("input"))]
            )

        # ⏱ delay (last task کے بعد نہیں)
        if i < len(tasks) - 1:
            smart_delay()


# ================= CLEAR =================
@app.post("/clear-tasks")
def clear_tasks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks")

    # 🔥 RESET AUTO INCREMENT
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")

    conn.commit()
    conn.close()

    return {"status": "cleared"}


@app.get("/vpns")
def get_vpns():
    return load_vpns()


# 🔥 TEST SCHEDULER (SAFE)
def test_scheduler():
    print("⏱ Scheduler running...")


@app.get("/browsers")
def get_browsers():

    START_PORT = 9222
    MAX = 200  # P1 → P200

    def check(i):
        port = START_PORT + i

        try:
            res = requests.get(f"http://127.0.0.1:{port}/json", timeout=0.05)

            if res.status_code == 200:
                return {"id": i + 1, "port": port}

        except:
            return None

    with ThreadPoolExecutor(max_workers=30) as ex:
        results = list(ex.map(check, range(MAX)))

    return [r for r in results if r]


@app.get("/screenshot/{port}")
def get_screenshot(port: int):

    try:
        tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

        ws_url = None

        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break

        if not ws_url:
            return {"error": "no tab"}

        ws = websocket.create_connection(ws_url)

        # ✅ ADD THIS BLOCK (یہاں ڈالنا ہے)
        # 1️⃣ پہلے metrics
        ws.send(json.dumps({"id": 2, "method": "Page.getLayoutMetrics"}))
        metrics = json.loads(ws.recv())

        width = metrics["result"]["layoutViewport"]["clientWidth"]
        height = metrics["result"]["layoutViewport"]["clientHeight"]

        scroll_y = metrics["result"]["visualViewport"]["pageY"]

        # 2️⃣ پھر screenshot WITH CLIP
        ws.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "Page.captureScreenshot",
                    "params": {
                        "format": "jpeg",
                        "quality": 50,
                        "clip": {
                            "x": 0,
                            "y": scroll_y,
                            "width": width,
                            "height": height,
                            "scale": 1,
                        },
                    },
                }
            )
        )

        result = json.loads(ws.recv())
        ws.close()

        img = result["result"]["data"]

        return {"image": img, "width": width, "height": height}

    except Exception as e:
        return {"error": str(e)}


@app.post("/click")
def click(data: dict):

    port = data.get("port")
    x = data.get("x")
    y = data.get("y")

    # 🔥 BROADCAST CLICK
    try:
        requests.post(
            "http://127.0.0.1:8000/broadcast_click",
            json={
                "x": data["x"],
                "y": data["y"],
                "targets": data.get("targets", []),
                "source": data.get("source"),
            },
        )
    except:
        pass

    try:
        tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

        ws_url = None
        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break

        if not ws_url:
            return {"error": "no tab"}

        ws = websocket.create_connection(ws_url)

        ws.send(json.dumps({"id": 2, "method": "Page.getLayoutMetrics"}))
        metrics = json.loads(ws.recv())

        scroll_y = metrics["result"]["visualViewport"]["pageY"]

        # 🔥 UNIQUE ID (FIX)
        ws.send(json.dumps({"id": 10, "method": "Page.getLayoutMetrics"}))
        layout = json.loads(ws.recv())

        offsetX = layout["result"]["layoutViewport"]["pageX"]
        offsetY = layout["result"]["layoutViewport"]["pageY"]

        x = x + offsetX
        y = y + offsetY

        # move mouse
        ws.send(
            json.dumps(
                {
                    "id": 11,
                    "method": "Input.dispatchMouseEvent",
                    "params": {"type": "mouseMoved", "x": x, "y": y + scroll_y},
                }
            )
        )

        # click down
        ws.send(
            json.dumps(
                {
                    "id": 12,
                    "method": "Input.dispatchMouseEvent",
                    "params": {
                        "type": "mousePressed",
                        "x": x,
                        "y": y,
                        "button": "left",
                        "clickCount": 1,
                    },
                }
            )
        )

        # click up
        ws.send(
            json.dumps(
                {
                    "id": 13,
                    "method": "Input.dispatchMouseEvent",
                    "params": {
                        "type": "mouseReleased",
                        "x": x,
                        "y": y,
                        "button": "left",
                    },
                }
            )
        )

        ws.close()

        return {"status": "clicked"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/broadcast_click")
def broadcast_click(data: dict):

    x = data.get("x")
    y = data.get("y")
    targets = data.get("targets", [])
    source = data.get("source", None)

    for t in targets:
        if source is not None and t == source:
            continue

        port = 9221 + t

        print("🔥 TARGET:", t, "PORT:", port)

        try:
            tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

            ws_url = None
            for tab in tabs:
                if tab.get("type") == "page":
                    ws_url = tab.get("webSocketDebuggerUrl")
                    break

            if not ws_url:
                continue

            ws = websocket.create_connection(ws_url)

            ws.send(
                json.dumps(
                    {
                        "id": 1,
                        "method": "Input.dispatchMouseEvent",
                        "params": {
                            "type": "mousePressed",
                            "x": x,
                            "y": y,
                            "button": "left",
                            "clickCount": 1,
                        },
                    }
                )
            )

            ws.send(
                json.dumps(
                    {
                        "id": 2,
                        "method": "Input.dispatchMouseEvent",
                        "params": {
                            "type": "mouseReleased",
                            "x": x,
                            "y": y,
                            "button": "left",
                            "clickCount": 1,
                        },
                    }
                )
            )

            ws.close()

        except Exception as e:
            print(e)

    return {"ok": True}


@app.post("/like_control")
def like_control(data: dict):

    target = data.get("target")
    action = data.get("action")  # START / STOP
    speed = float(data.get("speed", 1))

    port = 9221 + int(target)

    try:
        tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

        ws_url = None
        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break

        if not ws_url:
            print(f"[❌ NO TAB] Profile {target}")
            return {"ok": False}

        ws = websocket.create_connection(ws_url)

        # =========================
        # 🔥 YAHAN CODE ADD HOGA
        # =========================

        if action == "START":
            print(f"[START] Profile {target} speed={speed}")

            js = f"""
            (function(){{
                window.dispatchEvent(new CustomEvent("LIKE_EVENT", {{
                    detail: {{
                        type: "START",
                        speed: {speed}
                    }}
                }}));
            }})();
            """

        elif action == "STOP":
            print(f"[STOP] Profile {target}")

            js = """
            (function(){
                window.dispatchEvent(new CustomEvent("LIKE_EVENT", {
                    detail: {
                        type: "STOP"
                    }
                }));
            })();
            """

        # =========================

        ws.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {"expression": js},
                }
            )
        )

        ws.close()

    except Exception as e:
        print("LIKE ERROR:", e)

    return {"ok": True}


@app.post("/broadcast_scroll")
def broadcast_scroll(data: dict):

    delta = data["deltaY"]
    targets = data["targets"]
    source = data["source"]

    for t in targets:
        if t == source:
            continue

        port = 9221 + t

        try:
            tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

            ws_url = None
            for tab in tabs:
                if tab.get("type") == "page":
                    ws_url = tab.get("webSocketDebuggerUrl")
                    break

            if not ws_url:
                continue

            ws = websocket.create_connection(ws_url)

            ws.send(
                json.dumps(
                    {
                        "id": 1,
                        "method": "Input.dispatchMouseEvent",
                        "params": {"type": "mouseWheel", "deltaY": delta},
                    }
                )
            )

            ws.close()

        except:
            pass

    return {"ok": True}


@app.post("/broadcast_key")
def broadcast_key(data: dict):

    key = data.get("key")

    print("KEY RECEIVED:", key)

    targets = data.get("targets", [])

    for t in targets:

        port = 9221 + t  # ⚠️ یہی تمہارا correct port ہے

        try:
            tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

            ws_url = None
            for tab in tabs:
                if tab.get("type") == "page":
                    ws_url = tab.get("webSocketDebuggerUrl")
                    break

            if not ws_url:
                continue

            ws = websocket.create_connection(ws_url)

            # Detect special keys
            special_keys = {
                "Enter": {"key": "Enter", "code": "Enter"},
                "Backspace": {"key": "Backspace", "code": "Backspace"},
                "Tab": {"key": "Tab", "code": "Tab"},
                " ": {"key": " ", "code": "Space"},
            }

            if key in special_keys:
                params = {
                    "type": "keyDown",
                    "key": special_keys[key]["key"],
                    "code": special_keys[key]["code"],
                }
                params_up = {
                    "type": "keyUp",
                    "key": special_keys[key]["key"],
                    "code": special_keys[key]["code"],
                }
            elif len(key) == 1:
                params = {"type": "keyDown", "text": key}
                params_up = {"type": "keyUp", "text": key}
            else:
                continue

            ws.send(
                json.dumps(
                    {"id": 1, "method": "Input.dispatchKeyEvent", "params": params}
                )
            )

            ws.send(
                json.dumps(
                    {"id": 2, "method": "Input.dispatchKeyEvent", "params": params_up}
                )
            )

            ws.close()

        except Exception as e:
            print("KEY ERROR:", e)

    return {"ok": True}


@app.post("/type")
def type_text(data: dict):

    port = data.get("port")
    text = data.get("text")

    try:
        tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

        ws_url = None
        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break

        ws = websocket.create_connection(ws_url)

        for char in text:
            ws.send(
                json.dumps(
                    {
                        "id": 1,
                        "method": "Input.dispatchKeyEvent",
                        "params": {"type": "char", "text": char},
                    }
                )
            )

        ws.close()

        return {"status": "typed"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/reload")
def reload_browser(data: dict):
    try:
        port = data.get("port")

        tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

        ws_url = None
        for tab in tabs:
            if tab.get("type") == "page":
                ws_url = tab.get("webSocketDebuggerUrl")
                break

        if not ws_url:
            return {"error": "no tab"}

        ws = websocket.create_connection(ws_url)

        ws.send(json.dumps({"id": 1, "method": "Page.reload"}))

        ws.close()

        return {"status": "reloaded"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/broadcast_type")
def broadcast_type(data: dict):

    text = data["text"]
    targets = data["targets"]
    source = data["source"]

    for t in targets:
        if t == source:
            continue

        port = 9221 + t

        try:
            tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

            ws_url = None
            for tab in tabs:
                if tab.get("type") == "page":
                    ws_url = tab.get("webSocketDebuggerUrl")
                    break

            if not ws_url:
                continue

            ws = websocket.create_connection(ws_url)

            for char in text:
                ws.send(
                    json.dumps(
                        {
                            "id": 1,
                            "method": "Input.dispatchKeyEvent",
                            "params": {"type": "char", "text": char},
                        }
                    )
                )

            ws.close()

        except:
            pass

    return {"ok": True}


@app.post("/verify_user")
def verify_user(data: dict):
    email = data.get("email")

    user = get_user_from_db(email)

    if not user:
        return {"status": "invalid"}

    if user["status"] != "active":
        return {"status": "disabled"}

    return {"status": "ok", "timestamp": int(time.time())}


port = int(os.environ.get("PORT", 8000))

import uvicorn
import os

if __name__ == "__main__":
    start_listener()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


def check_expired_users():
    conn = get_db()
    cursor = conn.cursor()

    now = datetime.datetime.now()

    cursor.execute("SELECT id, expiry FROM users WHERE expiry IS NOT NULL")

    users = cursor.fetchall()

    for u in users:
        expiry = datetime.datetime.strptime(u["expiry"], "%Y-%m-%d")

        if now > expiry:
            cursor.execute("UPDATE users SET status='disabled' WHERE id=?", (u["id"],))

    conn.commit()
    conn.close()


# 🔥 RUN EVERY 1 HOUR
# add_interval_job(check_expired_users, 3600)


@app.post("/inject-js")
def inject_js(data: dict):

    targets = data.get("targets", [])
    script = data.get("script")

    for t in targets:
        port = 9221 + t

        try:
            tabs = requests.get(f"http://127.0.0.1:{port}/json").json()

            ws_url = None
            for tab in tabs:
                if tab.get("type") == "page":
                    ws_url = tab.get("webSocketDebuggerUrl")
                    break

            if not ws_url:
                continue

            ws = websocket.create_connection(ws_url)

            ws.send(
                json.dumps(
                    {
                        "id": 1,
                        "method": "Runtime.evaluate",
                        "params": {"expression": script},
                    }
                )
            )

            ws.close()

        except Exception as e:
            print("❌ inject error:", e)

    return {"status": "sent"}
