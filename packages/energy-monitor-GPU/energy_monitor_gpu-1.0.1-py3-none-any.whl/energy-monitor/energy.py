import pynvml
import time
import threading
import pymongo
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId


class EnergyMonitor:
    def __init__(self):
        # -----------------------------
        # Hardcoded MongoDB connection
        # -----------------------------
        MONGO_URI = "mongodb+srv://gayatri:12211312@energydb.et7jn.mongodb.net/?retryWrites=true&w=majority&appName=energydb"

        # Connect to MongoDB
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            print("✅ Database connected successfully")
        except Exception as e:
            raise ConnectionError(f"❌ Failed to connect to MongoDB: {e}")

        self.db = self.client["test"]
        self.users = self.db["users"]

        # Class attributes
        self.start_time = None
        self.running = False
        self.user_id = None
        self.project_name = None
        self.gpu_handle = None
        self.power_readings = []
        self.sampler_thread = None

    # -----------------------------
    # GPU Power Sampling Thread
    # -----------------------------
    def _sampler(self):
        """Background thread: sample GPU power every second"""
        while self.running:
            try:
                power_watts = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle) / 1000  # mW → W
                self.power_readings.append(power_watts)
            except Exception as e:
                print("⚠️ Sampling error:", e)
            time.sleep(1)

    # -----------------------------
    # Start Monitoring
    # -----------------------------
    def start(self, project_name: str):
        if self.running:
            print("⚠️ Monitoring is already running")
            return

        if not self.user_id:
            print("❌ Please log in first")
            return

        user_data = self.users.find_one({"_id": ObjectId(self.user_id)})
        if not user_data:
            print("❌ User not found")
            return

        if project_name not in user_data.get("projects", {}):
            create_project = input(f"Project '{project_name}' not found. Create a new project? (Y/N): ").strip().upper()
            if create_project != "Y":
                print("❌ Operation canceled")
                return

            self.users.update_one(
                {"_id": ObjectId(self.user_id)},
                {"$set": {f"projects.{project_name}": {}}}
            )

        # Initialize GPU
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except Exception as e:
            print(f"❌ NVML Initialization failed: {e}")
            return

        # Reset state
        self.power_readings = []
        self.start_time = time.time()
        self.running = True
        self.project_name = project_name

        # Start background thread
        self.sampler_thread = threading.Thread(target=self._sampler, daemon=True)
        self.sampler_thread.start()

        print(f"✅ Energy monitoring started for project: {project_name}")

    # -----------------------------
    # Stop Monitoring
    # -----------------------------
    def stop(self):
        if not self.running:
            print("⚠️ No active monitoring session to stop")
            return

        # Stop sampling
        self.running = False
        if self.sampler_thread:
            self.sampler_thread.join(timeout=2)

        end_time = time.time()
        duration = end_time - self.start_time

        # Calculate average power
        if self.power_readings:
            avg_power_watts = sum(self.power_readings) / len(self.power_readings)
        else:
            try:
                avg_power_watts = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle) / 1000
            except Exception:
                avg_power_watts = 0.0

        # Energy in kWh
        total_energy_kwh = (avg_power_watts * duration) / 3600

        pynvml.nvmlShutdown()

        if self.user_id:
            timestamp = datetime.utcnow()
            normalized_project_name = self.project_name.strip()

            user_data = self.users.find_one({"_id": ObjectId(self.user_id)})
            if not user_data:
                print("❌ User not found")
                return

            projects = user_data.get("projects", {})
            if normalized_project_name not in projects:
                projects[normalized_project_name] = {}

            project_data = projects[normalized_project_name]
            run_numbers = [
                int(key[3:]) for key in project_data if key.startswith("run") and key[3:].isdigit()
            ]
            next_run_number = max(run_numbers, default=0) + 1
            new_run_key = f"run{next_run_number}"

            # Save run data
            project_data[new_run_key] = {
                "timestamp": timestamp,
                "duration_sec": duration,
                "avg_power_watts": avg_power_watts,
                "energy_kwh": total_energy_kwh
            }

            projects[normalized_project_name] = project_data

            self.users.update_one(
                {"_id": ObjectId(self.user_id)},
                {"$set": {"projects": projects}}
            )

            print(f"✅ Energy data stored under {normalized_project_name} -> {new_run_key}")
            print(f"⏱ Duration: {duration:.1f} s")
            print(f"⚡ Avg Power: {avg_power_watts:.2f} W")
            print(f"🔋 Energy: {total_energy_kwh:.4f} kWh")

        else:
            print("⚠️ No logged-in user. Data not stored")

    # -----------------------------
    # Login Function
    # -----------------------------
    def login(self, username: str, password: str) -> bool:
        user = self.users.find_one({"username": username})

        if not user:
            print("❌ No username found")
            return False

        hashed_password = user.get("password")
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")

        if not bcrypt.checkpw(password.encode("utf-8"), hashed_password):
            print("❌ Password incorrect")
            return False

        self.user_id = str(user["_id"])
        print("✅ Login successful")
        return True
