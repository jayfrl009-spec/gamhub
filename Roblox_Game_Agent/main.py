import base64, io, json, os, threading, time, urllib.request
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import mss
from PIL import Image, ImageTk
from pynput.keyboard import Controller, Listener, Key

URL = "http://localhost:11434/api/generate"
ACTIONS = {"forward": "w", "back": "s", "left": "a", "right": "d", "jump": " "}
class App:
    def __init__(self, root):
        self.root=root; root.title("Roblox Game Agent"); root.geometry("820x620")
        root.configure(bg="#0b1020"); self.folder=""; self.stop=threading.Event()
        self.running=False; self.model=tk.StringVar(value="qwen2.5vl:3b"); self.allowed=tk.BooleanVar()
        tk.Label(root,text="ROBLOX GAME AGENT",font=("Segoe UI",18,"bold"),fg="#58a6ff",bg="#0b1020").pack(pady=10)
        tk.Button(root,text="Choose approved output folder",command=self.pick).pack()
        self.folder_label=tk.Label(root,text="No folder selected",fg="#fbbf24",bg="#0b1020"); self.folder_label.pack()
        row=tk.Frame(root,bg="#0b1020"); row.pack(pady=8)
        tk.Label(row,text="Ollama vision model:",fg="white",bg="#0b1020").pack(side="left")
        tk.Entry(row,textvariable=self.model,width=24).pack(side="left",padx=6)
        tk.Button(row,text="Observe",command=self.observe).pack(side="left",padx=4)
        tk.Button(row,text="Test AI",command=self.test_ai).pack(side="left",padx=4)
        self.preview=tk.Label(root,text="Observe to preview your screen",bg="#060912",fg="white",height=12); self.preview.pack(fill="both",expand=True,padx=12,pady=8)
        manual=tk.Frame(root,bg="#0b1020"); manual.pack()
        for label,act in [("W ↑","forward"),("S ↓","back"),("A ←","left"),("D →","right"),("SPACE","jump")]:
            tk.Button(manual,text=label,command=lambda a=act:self.tap(a)).pack(side="left",padx=3)
        tk.Button(manual,text="AI RUN (20 steps max)",command=self.run_ai,bg="#166534",fg="white").pack(side="left",padx=8)
        tk.Button(manual,text="STOP / F8",command=self.halt,bg="#b91c1c",fg="white").pack(side="left",padx=3)
        tk.Checkbutton(root,text="I will use this only where automation is permitted.",variable=self.allowed,bg="#0b1020",fg="white",selectcolor="#111a2e").pack(pady=6)
        self.status=tk.Label(root,text="Ready",fg="#93c5fd",bg="#0b1020"); self.status.pack()
        self.log=tk.Text(root,height=5,bg="#060912",fg="#cbd5e1"); self.log.pack(fill="x",padx=12,pady=8)
        self.keys=Controller()
        try:
            self.listener=Listener(on_press=self.on_key); self.listener.start()
        except Exception: self.listener=None
        root.protocol("WM_DELETE_WINDOW",self.close)
    def say(self,s):
        self.log.insert("end",f"{datetime.now().strftime('%H:%M:%S')} {s}\n"); self.log.see("end")
    def pick(self):
        p=filedialog.askdirectory(title="Choose the only folder this app may write to")
        if p: self.folder=os.path.abspath(p); self.folder_label.config(text=self.folder,fg="#86efac")
    def capture(self):
        with mss.mss() as s:
            m=s.monitors[1]; shot=s.grab(m)
            return Image.frombytes("RGB",shot.size,shot.rgb)
    def save(self,img):
        if not self.folder: raise ValueError("Choose an approved output folder first.")
        name="screen_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png"
        path=os.path.join(self.folder,name); img.save(path); return name
    def show(self,img):
        img.thumbnail((780,300)); self.pic=ImageTk.PhotoImage(img); self.preview.config(image=self.pic,text="",height=0)
    def observe(self):
        try:
            im=self.capture(); name=self.save(im); self.show(im); self.say("Saved "+name+" in approved folder."); self.status.config(text="Screen observed.")
        except Exception as e: messagebox.showerror("Observe failed",str(e))
    def ask_ai(self,img,prompt):
        b=io.BytesIO(); img.thumbnail((1024,1024)); img.save(b,format="JPEG",quality=80)
        data=json.dumps({"model":self.model.get().strip(),"prompt":prompt,"images":[base64.b64encode(b.getvalue()).decode()],"stream":False,"format":"json"}).encode()
        req=urllib.request.Request(URL,data=data,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read().decode()).get("response","")
    def test_ai(self):
        if not self.folder: messagebox.showwarning("Choose folder","Choose an approved output folder first."); return
        self.status.config(text="Testing local Ollama…")
        def work():
            try:
                ans=self.ask_ai(self.capture(),'Describe this screenshot in one sentence. Return JSON: {"description":"..."}')
                self.root.after(0,lambda:self.say("AI: "+ans[:400])); self.root.after(0,lambda:self.status.config(text="AI test succeeded."))
            except Exception as e:
                self.root.after(0,lambda:self.say("AI test failed: "+str(e))); self.root.after(0,lambda:self.status.config(text="Check Ollama and the model name."))
        threading.Thread(target=work,daemon=True).start()
    def tap(self,action):
        if self.running: return
        key=ACTIONS[action]
        def press():
            try: self.keys.press(key); time.sleep(.25)
            finally:
                try: self.keys.release(key)
                except Exception: pass
        threading.Thread(target=press,daemon=True).start()
    def run_ai(self):
        if not self.folder: messagebox.showwarning("Choose folder","Choose an approved output folder first."); return
        if not self.allowed.get(): messagebox.showwarning("Confirm permitted use","Check the permission box first."); return
        if self.running: return
        if not messagebox.askyesno("Confirm","AI may use short movement keys for up to 20 steps. Keep Roblox visible. F8 or STOP to end. Start?"): return
        self.stop.clear(); self.running=True; threading.Thread(target=self.loop,daemon=True).start()
    def loop(self):
        actions=set(ACTIONS)|{"wait"}
        try:
            for n in range(20):
                if self.stop.is_set(): break
                im=self.capture(); self.root.after(0,lambda im=im:self.show(im))
                prompt='Choose one safe short movement in this Roblox screenshot. Never use menus, chat, purchases, trading, or account screens. If unclear choose wait. Return JSON: {"action":"forward|back|left|right|jump|wait","seconds":0.3,"reason":"brief reason"}'
                try:
                    d=json.loads(self.ask_ai(im,prompt)); act=str(d.get("action","wait")).lower()
                    sec=max(.2,min(float(d.get("seconds",.3)),.8))
                    if act not in actions: act="wait"
                except Exception as e:
                    self.root.after(0,lambda e=e:self.say("AI stopped: "+str(e))); break
                self.root.after(0,lambda n=n,act=act:self.say(f"Step {n+1}/20: {act}"))
                if act in ACTIONS:
                    self.keys.press(ACTIONS[act]); time.sleep(sec); self.keys.release(ACTIONS[act])
                else: time.sleep(sec)
                time.sleep(.35)
        finally:
            self.running=False; self.root.after(0,lambda:self.status.config(text="Stopped or 20-step limit reached."))
    def halt(self):
        self.stop.set()
        for k in ["w","a","s","d"," "]:
            try: self.keys.release(k)
            except Exception: pass
        self.status.config(text="STOP requested."); self.say("STOP requested.")
    def on_key(self,key):
        if key==Key.f8:
            self.stop.set()
            for k in ["w","a","s","d"," "]:
                try: self.keys.release(k)
                except Exception: pass
            return False
    def close(self):
        self.halt()
        try:
            if self.listener: self.listener.stop()
        except Exception: pass
        self.root.destroy()
if __name__=="__main__":
    r=tk.Tk(); App(r); r.mainloop()
