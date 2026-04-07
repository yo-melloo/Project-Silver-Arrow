"""
Dynamic RPM Thresholds Calculator
Calcula limites de rotação baseado no maxRpm do carro (de cada fabricante)
Sincronizado com dashboard web via argentum_bridge
"""

import struct
import mmap
from typing import Dict, Optional


class RPMThresholdCalculator:
    """
    Calcula thresholds dinâmicos baseado no maxRpm do carro
    
    Exemplo:
    - Ferrari: maxRpm=8000  → warning=6000, critical=7200, redline=8000
    - SUV: maxRpm=5500     → warning=4125, critical=4950, redline=5500
    - F1: maxRpm=15000     → warning=11250, critical=13500, redline=15000
    """
    
    # Percentuais de thresholds relativos ao maxRpm
    # Esses percentuais funcionam bem para a maioria dos carros
    THRESHOLD_PERCENTAGES = {
        "warning": 0.75,    # 75% do maxRpm
        "critical": 0.90,   # 90% do maxRpm
        "redline": 1.00,    # 100% (maxRpm)
        "idle": 0.15,       # 15% do maxRpm (rotação baixa)
    }
    
    def __init__(self):
        self.max_rpm = 10000  # Default
        self.car_name = "UNKNOWN"
        self.thresholds = self._calculate_thresholds(10000)
        
    def read_from_ac_shared_memory(self) -> bool:
        """
        Lê maxRpm e car_name diretamente do AC shared memory
        Retorna True se conseguiu ler, False caso contrário
        """
        try:
            static_map = mmap.mmap(0, 1024, "acpmf_static", access=mmap.ACCESS_READ)
            
            # Car name at offset 68 (66 bytes, utf-16)
            static_map.seek(68)
            car_bytes = static_map.read(66)
            self.car_name = car_bytes.decode('utf-16').split('\0')[0].strip()
            
            # Max RPM at offset 412 (int32)
            static_map.seek(412)
            max_rpm_raw = struct.unpack("i", static_map.read(4))[0]
            
            # Validação: maxRpm deve ser entre 3000 e 20000
            if 3000 <= max_rpm_raw <= 20000:
                self.max_rpm = max_rpm_raw
                self.thresholds = self._calculate_thresholds(self.max_rpm)
                static_map.close()
                return True
            else:
                self.max_rpm = 10000
                static_map.close()
                return False
                
        except Exception:
            return False
    
    def _calculate_thresholds(self, max_rpm: int) -> Dict[str, int]:
        """Calcula thresholds como percentual do maxRpm"""
        return {
            "idle": max(1000, int(max_rpm * self.THRESHOLD_PERCENTAGES["idle"])),
            "warning": int(max_rpm * self.THRESHOLD_PERCENTAGES["warning"]),
            "critical": int(max_rpm * self.THRESHOLD_PERCENTAGES["critical"]),
            "redline": max_rpm,
        }
    
    def get_thresholds(self) -> Dict[str, int]:
        """Retorna thresholds calculados"""
        return self.thresholds
    
    def get_info(self) -> Dict:
        """Retorna informações do carro e thresholds"""
        return {
            "car": self.car_name,
            "max_rpm": self.max_rpm,
            "thresholds": self.thresholds,
            "percentages": self.THRESHOLD_PERCENTAGES,
        }
    
    def classify_rpm_percentage(self, rpm: int) -> float:
        """
        Retorna o percentual de RPM (0.0 a 1.0)
        Útil para animações e barra de progresso no dashboard
        """
        return min(1.0, rpm / max(self.max_rpm, 1))
    
    def get_rpm_state_description(self, rpm: int) -> str:
        """
        Retorna descrição do estado do RPM
        Usa thresholds dinâmicos
        """
        t = self.thresholds
        
        if rpm < t["idle"]:
            return "Idle"
        elif rpm < t["warning"]:
            return "OK"
        elif rpm < t["critical"]:
            return "Rising"
        elif rpm < t["redline"]:
            return "Warning"
        else:
            return "Redline!"


class DynamicRPMConfig:
    """
    Configuração dinâmica que combina AC shared memory + json config
    Mantém compatibilidade com rgb_config.json mas usa valores do AC
    """
    
    def __init__(self, config_dict: Dict = None):
        """
        Initialize with optional config dict from rgb_config.json
        
        Args:
            config_dict: Configuração estática do arquivo JSON
        """
        self.static_config = config_dict or {}
        self.calculator = RPMThresholdCalculator()
        self.use_dynamic = True
        
        # Tenta ler do AC
        if not self.calculator.read_from_ac_shared_memory():
            # Fallback: usa valores estáticos do JSON ou padrões
            self.use_dynamic = False
    
    def get_thresholds(self) -> Dict[str, int]:
        """
        Retorna thresholds: dinâmicos se AC disponível, senão usa JSON
        """
        if self.use_dynamic:
            return self.calculator.get_thresholds()
        else:
            # Fallback para configuração estática
            return self.static_config.get("shift_light_thresholds", {
                "idle": 2000,
                "warning": 6000,
                "critical": 8000,
                "redline": 9000,
            })
    
    def get_car_info(self) -> Dict:
        """Retorna informações do carro"""
        if self.use_dynamic:
            return {
                "name": self.calculator.car_name,
                "max_rpm": self.calculator.max_rpm,
                "source": "AC Shared Memory",
            }
        else:
            return {
                "name": "Unknown",
                "max_rpm": 10000,
                "source": "Default Config",
            }
    
    def update_from_ac(self) -> bool:
        """
        Atualiza thresholds lendo novamente do AC
        Useful para quando o carro muda (mudança de car mid-game)
        
        Returns:
            True se conseguiu atualizar, False caso contrário
        """
        if self.calculator.read_from_ac_shared_memory():
            self.use_dynamic = True
            return True
        return False
    
    def get_telemetry_sync_data(self) -> Dict:
        """
        Retorna dados para sincronizar com dashboard web
        (mesmo que seria enviado pelo argentum_bridge)
        """
        thresholds = self.get_thresholds()
        car_info = self.get_car_info()
        
        return {
            "car": car_info["name"],
            "maxRpm": car_info["max_rpm"],
            "thresholds": thresholds,
            "colors": self.static_config.get("color_scheme", {
                "idle": [0, 255, 0],
                "warning": [255, 255, 0],
                "critical": [255, 128, 0],
                "redline": [255, 0, 0],
            }),
            "sync": True,
        }


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("Dynamic RPM Calculator Test")
    print("=" * 60)
    
    calc = RPMThresholdCalculator()
    
    if calc.read_from_ac_shared_memory():
        print(f"\n✓ AC Connected")
        print(f"  Car: {calc.car_name}")
        print(f"  MaxRPM: {calc.max_rpm}")
        print(f"\nCalculated Thresholds:")
        
        info = calc.get_info()
        for key, value in info["thresholds"].items():
            percent = info["percentages"][key] * 100
            print(f"  {key:12s}: {value:5d} RPM ({percent:5.1f}%)")
        
        # Test classification
        print(f"\nRPM Classification Test:")
        test_rpms = [1000, 3000, 6000, 8000, 9000]
        for rpm in test_rpms:
            if rpm <= calc.max_rpm:
                pct = calc.classify_rpm_percentage(rpm)
                desc = calc.get_rpm_state_description(rpm)
                print(f"  {rpm:5d} RPM: {pct*100:5.1f}% → {desc}")
    else:
        print("✗ AC not connected, using defaults")
        info = calc.get_info()
        print(f"  Default thresholds: {info['thresholds']}")
    
    print("\n" + "=" * 60)
