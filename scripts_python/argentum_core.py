import os
import time
import random
import mmap
import struct
from datetime import datetime

def format_car_name(name: str) -> str:
    """Formata o nome do carro de 'nome_do_carro' para 'Nome Do Carro'"""
    if not name:
        return "UNKNOWN"
    # Remove underscores e converte para title case (capitalizado)
    formatted = name.replace("_", " ").title()
    return formatted

class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m' 
    BOLD = '\033[1m'
    PISCAR = '\033[5m'

class AssettoCorsaProvider:
    """Real Data Provider: Lê Physics e Static do Assetto Corsa."""
    def __init__(self):
        self.physics_map = None
        self.static_map = None
        self.connected = False
        self.pilot_name = "SEARCHING..."
        self.max_rpm = 10000

    def connect(self):
        try:
            # Tags confirmadas pelo usuário: acpmf_physics e acpmf_static
            self.physics_map = mmap.mmap(0, 1024, "acpmf_physics", access=mmap.ACCESS_READ)
            self.static_map = mmap.mmap(0, 1024, "acpmf_static", access=mmap.ACCESS_READ)
            self.connected = True
            self._load_static_info()
            return True
        except Exception:
            self.connected = False
            return False


    def _load_static_info(self):
        try:
            # Pilot name at offset 200 (66 bytes, utf-16) - FUNCIONA
            self.static_map.seek(200)
            name_bytes = self.static_map.read(66)
            self.pilot_name = name_bytes.decode('utf-16').split('\0')[0].strip()
            
            # Car model at offset 68 (66 bytes, utf-16) - CONFIRMADO ✓
            self.static_map.seek(68)
            car_bytes = self.static_map.read(66)
            raw_car_name = car_bytes.decode('utf-16').split('\0')[0].strip()
            self.car_model = format_car_name(raw_car_name)
            
            # Max RPM at offset 412 (int) - CONFIRMADO ✓
            self.static_map.seek(412)
            self.max_rpm = struct.unpack("i", self.static_map.read(4))[0]
            if self.max_rpm <= 0 or self.max_rpm > 20000:
                self.max_rpm = 10000
        except:
            self.pilot_name = "AC_PILOT"
            self.car_model = "UNKNOWN"
            self.max_rpm = 10000

    def fetch(self):
        if not self.connected:
            if not self.connect():
                return None

        try:
            # Estrutura correta do Physics map do AC:
            # Offset 0:  packetId(i)
            # Offset 4:  gas(f), brake(f), fuel(f)
            # Offset 16: gear(i), rpms(i)
            # Offset 24: steerAngle(f), speedKmh(f)
            # Offset 32: velocity[3](f), accG[3](f)
            # Offset 328: clutch(f) - clutch está no final da estrutura!
            
            self.physics_map.seek(0)
            buffer = self.physics_map.read(340)  # Lendo bytes suficientes
            
            packet = struct.unpack_from("i", buffer, 0)[0]
            gas = struct.unpack_from("f", buffer, 4)[0]
            brake = struct.unpack_from("f", buffer, 8)[0]
            gear_raw = struct.unpack_from("i", buffer, 16)[0]
            rpm = struct.unpack_from("i", buffer, 20)[0]
            steer = struct.unpack_from("f", buffer, 24)[0]
            speed = struct.unpack_from("f", buffer, 28)[0]
            clutch = struct.unpack_from("f", buffer, 328)[0]  # Clutch no offset 328

            # Tratamento de marchas: 0=R, 1=N, 2=1st, etc
            m_gear = gear_raw - 1
            gear_str = "R" if m_gear == -1 else ("N" if m_gear == 0 else str(m_gear))

            return {
                "source": "SIMULATOR (AC)",
                "pilot": self.pilot_name,
                "car": self.car_model,
                "packet": packet,
                "rpm": rpm,
                "max_rpm": self.max_rpm,
                "speed": int(speed),
                "gear": gear_str,
                "throttle": round(gas * 100, 1),
                "brake": round(brake * 100, 1),
                "clutch": round(clutch * 100, 1),
                "steer": round(steer * 450, 2),
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
        except Exception:
            self.connected = False
            return None
    
class TelemetryProvider:
    def __init__(self):
        self.rpm = 1000
        self.speed = 0
        self.gear = 1
        self.max_rpm = 10000
        self.packet = 0

    def fetch(self):
        self.packet += 1
        self.rpm += 350
        if self.rpm > self.max_rpm:
            self.rpm = 3000
            self.gear = (self.gear % 6) + 1
        self.speed = (self.rpm // 40) + (self.gear * 20)
        
        return {
            "source": "MOCK_MODE (DEMO)",
            "pilot": os.getenv("PILOT_NAME", "GENERIC_PILOT"),
            "car": "Ferrari F430",
            "packet": self.packet,
            "rpm": self.rpm,
            "max_rpm": self.max_rpm,
            "speed": self.speed,
            "gear": str(self.gear),
            "throttle": random.uniform(0, 100),
            "brake": 0,
            "clutch": 0,
            "steer": 0,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
        }

class ArgentumBuddy:
    def __init__(self):
        self.eye_states = [">  o  <", ">  O  <", ">  -  <", ">  ^  <"]

    def get_shift_light(self, rpm_pct):
        # Shift light progressiva de 0 a 100%
        pct = int(rpm_pct * 100)  # 0-100
        
        if pct < 60:
            # Verde: 0-59%
            filled = pct // 6  # 0-9 blocos
            bar = "■" * filled + "_" * (10 - filled)
            return f"{Cores.VERDE}[{bar}]{Cores.RESET}"
        elif pct < 85:
            # Amarelo: 60-84%
            filled = (pct - 60) // 3 + 6  # 6-9 blocos
            bar = "■" * filled + "_" * (10 - filled)
            return f"{Cores.AMARELO}[{bar}]{Cores.RESET}"
        elif pct < 95:
            # Vermelho: 85-94%
            filled = (pct - 85) // 2 + 8  # 8-9 blocos
            bar = "■" * filled + "_" * (10 - filled)
            return f"{Cores.VERMELHO}[{bar}]{Cores.RESET}"
        else:
            # Vermelho piscante: 95-100%
            return Cores.VERMELHO + Cores.BOLD + Cores.PISCAR + "[! ! ! ! ! ! ! ! ! !]" + Cores.RESET

    def render(self, rpm_pct):
        eye = random.choice(self.eye_states) if random.random() > 0.85 else ">  o  <"
        return fr"""
          {Cores.AZUL}___{Cores.RESET}
      {Cores.AZUL}___/   \___{Cores.RESET}
     {Cores.AZUL}/   {Cores.RESET}{eye}{Cores.AZUL}   \{Cores.RESET}
    {Cores.AZUL}|{Cores.RESET}  [#####]  {Cores.AZUL}|{Cores.RESET}
     {Cores.AZUL}\___     ___/{Cores.RESET}
         {Cores.AZUL}\___/{Cores.RESET}
        """

class ArgentumUI:
    def __init__(self):
        self.buddy = ArgentumBuddy()

    def clear_screen(self):
        # ANSI Escape Code: Volta ao topo e limpa
        print("\033[H\033[J", end="")

    def draw(self, data):
        if not data: return
        
        rpm_pct = data['rpm'] / data['max_rpm'] if data['max_rpm'] > 0 else 0
        shift_ui = self.buddy.get_shift_light(rpm_pct)
        buddy_ascii = self.buddy.render(rpm_pct)
        lines = buddy_ascii.strip().split('\n')
        
        self.clear_screen()
        
        print(f"\n    {Cores.BOLD}ARGENTUM CORE v1.3{Cores.RESET} | {Cores.AZUL}{data['timestamp']}{Cores.RESET}")
        print(f"    {'='*65}")
        print(f"    SOURCE: {Cores.AZUL}{data['source']}{Cores.RESET} | PILOTO: {Cores.BOLD}{data['pilot']}{Cores.RESET} | CARRO: {Cores.BOLD}{data['car']}{Cores.RESET} | PKT: {data['packet']}")
        print(f"    {'-'*65}")

        info_main = [
            f"MARCHA: {Cores.BOLD}{data['gear']:<8}{Cores.RESET}",
            f"SPEED : {Cores.BOLD}{data['speed']:3d} KM/H{Cores.RESET}",
            f"RPM   : {Cores.BOLD}{data['rpm']:5d}{Cores.RESET} / {data['max_rpm']}",
            f"SHIFT : {shift_ui}",
        ]
        
        for i, line in enumerate(lines):
            main_info = info_main[i] if i < len(info_main) else ""
            print(f"  {line}    {main_info}")
        
        # Telemetria de Pedais
        t_bar = "|" * int(data['throttle']/10)
        b_bar = "|" * int(data['brake']/10)
        c_bar = "|" * int(data['clutch']/10)
        
        print(f"    {'-'*65}")
        print(f"    GAS   : {Cores.VERDE}{t_bar:<10}{Cores.RESET} {data['throttle']:>5}%")
        print(f"    BRAKE : {Cores.VERMELHO}{b_bar:<10}{Cores.RESET} {data['brake']:>5}%")
        print(f"    CLUTCH: {Cores.AMARELO}{c_bar:<10}{Cores.RESET} {data['clutch']:>5}%")
        
        # Steering Visual
        steer = data['steer']
        s_pos = int((steer / 450) * 10) # Normalizado para barra de 10
        s_bar = [" "] * 21
        s_bar[10] = "|"
        idx = max(0, min(20, 10 + s_pos))
        s_bar[idx] = "X"
        
        print(f"    STEER : [ {''.join(s_bar)} ] {steer:>7.1f}°")
        print(f"    {'-'*65}")
        print(f"    {Cores.AZUL}[CTRL+C]{Cores.RESET} para encerrar a sessão.")

class ArgentumEngine:
    def __init__(self, provider, ui, target_fps=20):
        self.provider = provider
        self.ui = ui
        self.interval = 1.0 / target_fps
        self.running = False

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.running = True
        try:
            while self.running:
                start_time = time.time()
                data = self.provider.fetch()
                if data:
                    self.ui.draw(data)
                
                elapsed = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        print(f"\n{Cores.AMARELO}[ARGENTUM]{Cores.RESET} Sessão encerrada.")

if __name__ == "__main__":
    ac = AssettoCorsaProvider()
    mock = TelemetryProvider()
    ui = ArgentumUI()
    
    # Prioridade para o AC
    if ac.connect():
        provider = ac
    else:
        provider = mock
        
    engine = ArgentumEngine(provider, ui, target_fps=20)
    engine.start()
