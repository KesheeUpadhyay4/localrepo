import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import webbrowser
import threading
import re

# Optional text-to-speech. The app still works if this package is not installed.
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    TTS_AVAILABLE = False

# Optional microphone support. Text chat works without these packages.
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_AVAILABLE = False


APP_TITLE = "Personal AI Voice Assistant"

JOB_SITES = [
    ("LinkedIn Jobs", "https://www.linkedin.com/jobs/"),
    ("Naukri", "https://www.naukri.com/"),
    ("Indeed India", "https://in.indeed.com/"),
    ("Internshala", "https://internshala.com/"),
    ("Wellfound (startup jobs)", "https://wellfound.com/jobs"),
    ("Foundit", "https://www.foundit.in/"),
]

LEARNING_SITES = [
    ("GitHub", "https://github.com/"),
    ("Coursera", "https://www.coursera.org/"),
    ("Google Career Certificates", "https://grow.google/certificates/"),
]


class PersonalAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("950x680")
        self.root.minsize(760, 560)
        self.root.configure(bg="#f3f6fb")

        self.engine = None
        self.speaking_enabled = TTS_AVAILABLE

        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 175)
                self.engine.setProperty("volume", 0.9)
            except Exception:
                self.engine = None
                self.speaking_enabled = False

        self.build_ui()
        self.add_message(
            "Assistant",
            "Hello! I am your Personal AI Assistant. You can type a question "
            "or use Listen if microphone support is installed. Type 'help' "
            "to see what I can do."
        )

    def build_ui(self):
        header = tk.Frame(self.root, bg="#f3f6fb")
        header.pack(fill="x", padx=24, pady=(18, 8))

        tk.Label(
            header, text="PERSONAL AI VOICE ASSISTANT",
            font=("Segoe UI", 22, "bold"), fg="#17365d", bg="#f3f6fb"
        ).pack()

        tk.Label(
            header, text="Your personal desktop assistant",
            font=("Segoe UI", 11), fg="#536579", bg="#f3f6fb"
        ).pack(pady=(4, 5))

        self.status_label = tk.Label(
            header, text="Status: Ready", font=("Segoe UI", 10, "bold"),
            fg="#218838", bg="#f3f6fb"
        )
        self.status_label.pack()

        self.chat = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Segoe UI", 11),
            bg="white", fg="#202833", relief=tk.FLAT,
            padx=14, pady=12, state=tk.DISABLED
        )
        self.chat.pack(fill="both", expand=True, padx=24, pady=12)

        input_frame = tk.Frame(self.root, bg="#f3f6fb")
        input_frame.pack(fill="x", padx=24, pady=(0, 8))

        self.input_box = tk.Entry(
            input_frame, font=("Segoe UI", 12), relief=tk.FLAT,
            bg="white"
        )
        self.input_box.pack(side="left", fill="x", expand=True, ipady=12)
        self.input_box.bind("<Return>", lambda event: self.send_message())
        self.input_box.focus_set()

        button_frame = tk.Frame(self.root, bg="#f3f6fb")
        button_frame.pack(pady=(0, 12))

        tk.Button(
            button_frame, text="🎤 LISTEN", command=self.listen,
            font=("Segoe UI", 10, "bold"), bg="#1769aa", fg="white",
            activebackground="#12558b", activeforeground="white",
            relief=tk.FLAT, padx=22, pady=10, cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame, text="SEND", command=self.send_message,
            font=("Segoe UI", 10, "bold"), bg="#168653", fg="white",
            activebackground="#116b42", activeforeground="white",
            relief=tk.FLAT, padx=28, pady=10, cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame, text="CLEAR", command=self.clear_chat,
            font=("Segoe UI", 10, "bold"), bg="#596579", fg="white",
            activebackground="#414d60", activeforeground="white",
            relief=tk.FLAT, padx=25, pady=10, cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Label(
            self.root,
            text="Try: 'I need an AI internship', 'Where can I find jobs?', "
                 "'What time is it?', 'Open YouTube', or 'Search Python'",
            font=("Segoe UI", 9), fg="#66758a", bg="#f3f6fb"
        ).pack(pady=(0, 12))

    def add_message(self, sender, message):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat.see(tk.END)
        self.chat.configure(state=tk.DISABLED)

    def set_status(self, message, color="#218838"):
        self.status_label.config(text=f"Status: {message}", fg=color)

    def speak(self, message):
        if self.engine is None:
            return

        def worker():
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def contains_any(text, phrases):
        return any(phrase in text for phrase in phrases)

    def format_job_sites(self):
        lines = ["Here are useful websites for jobs and internships in India:"]
        for name, url in JOB_SITES:
            lines.append(f"• {name}: {url}")
        lines.append(
            "\nFor AI and Data Science roles, search for: "
            "AI/ML Intern, Python Developer Intern, Data Analyst Intern, "
            "Data Science Intern, and Junior Python Developer."
        )
        lines.append(
            "\nTip: Check the company, eligibility, stipend, location and "
            "application deadline before applying. Never pay money to get a job."
        )
        return "\n".join(lines)

    def get_response(self, user_text):
        text = user_text.lower().strip()
        cleaned = re.sub(r"[^\w\s]", " ", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if not cleaned:
            return "Please type a question or press Listen."

        # Greetings
        if cleaned in {"hi", "hello", "hey", "good morning", "good afternoon",
                       "good evening"}:
            return ("Hello! How can I help you? You can ask about jobs, "
                    "internships, time, date, websites or general web searches.")

        # Help
        if self.contains_any(cleaned, ["help", "what can you do", "commands"]):
            return (
                "I can help with these tasks:\n"
                "• Find job and internship websites\n"
                "• Suggest AI/ML and Python job search keywords\n"
                "• Tell you the current date and time\n"
                "• Open Google, YouTube, Gmail, GitHub or LinkedIn\n"
                "• Search the web for a topic\n\n"
                "If I cannot answer a question directly, I can search Google for it."
            )

        # Jobs / internships
        job_words = ["job", "jobs", "employment", "career", "vacancy",
                     "vacancies", "hiring", "work opportunity", "job opportunity"]
        internship_words = ["internship", "internships", "intern", "stipend"]
        if self.contains_any(cleaned, job_words + internship_words):
            return self.format_job_sites()

        # Resume / interview
        if self.contains_any(cleaned, ["resume", "cv", "curriculum vitae"]):
            return (
                "For a fresher resume, include your education, technical skills, "
                "projects, internships, certifications and contact details. "
                "Keep it clear and preferably one page. You can search "
                "' fresher AI ML resume examples' online."
            )

        if self.contains_any(cleaned, ["interview", "placement preparation"]):
            return (
                "For an AI/ML fresher interview, prepare Python, SQL, OOP, "
                "basic DSA, statistics, machine learning concepts and a clear "
                "explanation of your projects. Practise explaining what you "
                "built, your role, tools used and results."
            )

        # Date and time
        if self.contains_any(cleaned, ["time", "what time", "current time"]):
            return "The current time is " + datetime.now().strftime("%I:%M %p") + "."

        if self.contains_any(cleaned, ["date", "today's date", "today date", "what day"]):
            return "Today is " + datetime.now().strftime("%A, %d %B %Y") + "."

        # Open common websites
        sites = {
            "youtube": "https://www.youtube.com/",
            "google": "https://www.google.com/",
            "gmail": "https://mail.google.com/",
            "github": "https://github.com/",
            "linkedin": "https://www.linkedin.com/",
            "naukri": "https://www.naukri.com/",
            "internshala": "https://internshala.com/",
        }
        for site_name, url in sites.items():
            if (("open " + site_name) in cleaned
                    or ("launch " + site_name) in cleaned
                    or cleaned == site_name):
                webbrowser.open(url)
                return f"Opening {site_name.title()} in your browser."

        # Search web
        search_triggers = ["search for ", "search ", "google ", "look up "]
        for trigger in search_triggers:
            if cleaned.startswith(trigger):
                query = cleaned[len(trigger):].strip()
                if query:
                    webbrowser.open(
                        "https://www.google.com/search?q=" +
                        __import__("urllib.parse", fromlist=["quote"]).quote(query)
                    )
                    return f"I opened Google search results for: {query}"

        # Unknown question: offer a real web search rather than a fake answer.
        return (
            "I do not have a built-in answer for that question yet. "
            "I can search the web for it. Try typing: Search " + user_text
        )

    def send_message(self):
        user_text = self.input_box.get().strip()
        if not user_text:
            return

        self.input_box.delete(0, tk.END)
        self.add_message("You", user_text)

        response = self.get_response(user_text)
        self.add_message("Assistant", response)
        self.speak(response)

    def clear_chat(self):
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state=tk.DISABLED)
        self.add_message("Assistant", "Chat cleared. What would you like to do?")

    def listen(self):
        if not SPEECH_AVAILABLE:
            messagebox.showinfo(
                "Microphone setup",
                "Text chat is ready. To enable microphone input, install "
                "SpeechRecognition and PyAudio:\n\n"
                "python -m pip install SpeechRecognition pyaudio\n\n"
                "Then restart this application. If PyAudio installation "
                "fails, continue using the text box."
            )
            return

        def microphone_worker():
            try:
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    self.root.after(
                        0, lambda: self.set_status("Listening... Speak now", "#1769aa")
                    )
                    recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)

                self.root.after(
                    0, lambda: self.set_status("Recognizing speech...", "#1769aa")
                )
                recognized_text = recognizer.recognize_google(audio)

                def fill_and_send():
                    self.input_box.delete(0, tk.END)
                    self.input_box.insert(0, recognized_text)
                    self.set_status("Ready")
                    self.send_message()

                self.root.after(0, fill_and_send)

            except sr.WaitTimeoutError:
                self.root.after(
                    0, lambda: self.set_status("Ready - no speech detected", "#b36b00")
                )
                self.root.after(
                    0, lambda: messagebox.showwarning(
                        "No speech detected", "Please press Listen and speak clearly."
                    )
                )
            except sr.UnknownValueError:
                self.root.after(
                    0, lambda: self.set_status("Ready - speech not understood", "#b36b00")
                )
                self.root.after(
                    0, lambda: messagebox.showwarning(
                        "Could not understand", "Please try again or type your question."
                    )
                )
            except Exception as error:
                self.root.after(0, lambda: self.set_status("Microphone error", "#b00020"))
                self.root.after(
                    0, lambda: messagebox.showerror(
                        "Microphone error",
                        f"{error}\n\nCheck Windows microphone permission and make "
                        "sure no other app is using the microphone."
                    )
                )

        threading.Thread(target=microphone_worker, daemon=True).start()


if __name__ == "__main__":
    window = tk.Tk()
    app = PersonalAssistant(window)
    window.mainloop()
