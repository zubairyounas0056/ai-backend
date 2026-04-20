import json
import os

VPN_FILE = "vpn_storage.json"


# 🔹 LOAD VPNs
def load_vpns():
    if not os.path.exists(VPN_FILE):
        return []

    with open(VPN_FILE, "r") as f:
        return json.load(f)


def get_vpn_by_id(vpn_id):
    vpns = load_vpns()
    return next((vpn for vpn in vpns if vpn["id"] == vpn_id), None)


# 🔹 SAVE VPNs
def save_vpns(vpns):
    with open(VPN_FILE, "w") as f:
        json.dump(vpns, f, indent=4)


# 🔹 ADD VPN
def add_vpn(vpn_id, name, logo=None):
    vpns = load_vpns()

    # prevent duplicate
    for vpn in vpns:
        if vpn["id"] == vpn_id:
            return {"status": "exists"}

    vpns.append({"id": vpn_id, "name": name, "logo": logo})

    save_vpns(vpns)

    return {"status": "added"}


# 🔹 REMOVE VPN
def remove_vpn(vpn_id):
    vpns = load_vpns()
    vpns = [v for v in vpns if v["id"] != vpn_id]

    save_vpns(vpns)

    return {"status": "removed"}
