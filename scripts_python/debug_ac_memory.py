import mmap
import struct
import os
from datetime import datetime

class DebugLogger:
    """Escreve logs em arquivo e console simultaneamente."""
    def __init__(self, filename="debug_ac_memory.txt"):
        self.filename = filename
        self.file = open(filename, "w", encoding="utf-8")
        
    def write(self, message=""):
        """Escreve no console E no arquivo."""
        print(message)
        self.file.write(message + "\n")
        self.file.flush()
    
    def close(self):
        """Fecha o arquivo."""
        self.file.close()

def is_readable_string(s):
    """Verifica se uma string é legível (remove muito lixo)."""
    if not s or len(s) < 2:
        return False
    printable = sum(1 for c in s if c.isprintable() or c in '\t\n\r ')
    return printable / len(s) > 0.7

def analyze_offset(data, offset, max_len=256):
    """Analisa um offset e tenta extrair informações úteis."""
    results = []
    
    # Tenta como string UTF-16 LE
    try:
        raw = data[offset:offset+max_len]
        decoded = raw.decode('utf-16-le', errors='ignore').split('\0')[0]
        if is_readable_string(decoded):
            results.append(('UTF-16 LE', decoded[:80]))
    except:
        pass
    
    # Tenta como string UTF-8
    try:
        raw = data[offset:offset+max_len]
        decoded = raw.decode('utf-8', errors='ignore').split('\0')[0]
        if is_readable_string(decoded):
            results.append(('UTF-8', decoded[:80]))
    except:
        pass
    
    # Tenta como inteiro (4 bytes)
    try:
        if offset + 4 <= len(data):
            val = struct.unpack("i", data[offset:offset+4])[0]
            if val != 0:
                results.append(('INT32', f"{val} (0x{val:08x})"))
    except:
        pass
    
    # Tenta como unsigned int (4 bytes)
    try:
        if offset + 4 <= len(data):
            val = struct.unpack("I", data[offset:offset+4])[0]
            if val != 0 and val < 2**31:
                results.append(('UINT32', f"{val} (0x{val:08x})"))
    except:
        pass
    
    # Tenta como float (4 bytes)
    try:
        if offset + 4 <= len(data):
            val = struct.unpack("f", data[offset:offset+4])[0]
            if not (val == 0 or val == 1.0 or val != val):  # Ignora 0, 1, NaN
                if -1000 < val < 1000:
                    results.append(('FLOAT32', f"{val:.4f}"))
    except:
        pass
    
    # Tenta como short (2 bytes)
    try:
        if offset + 2 <= len(data):
            val = struct.unpack("h", data[offset:offset+2])[0]
            if val != 0:
                results.append(('INT16', f"{val}"))
    except:
        pass
    
    return results

def debug_ac_static():
    """Debug script para analisar TODOS os offsets do Static Map do AC."""
    log = DebugLogger(f"debug_ac_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    try:
        # AC usa tamanho fixo de 1024 bytes para static map
        # Valores baseados em argentum_core.py que está funcionando
        static_map = mmap.mmap(0, 1024, "acpmf_static", access=mmap.ACCESS_READ)
        total_size = 1024
        log.write(f"✓ Mmap 'acpmf_static' aberto com sucesso (tamanho: {total_size} bytes)")
        
        log.write("=" * 100)
        log.write(f"AC STATIC MAP DEBUG - Analisando TODOS os {total_size} bytes")
        log.write("=" * 100)
        log.write()
        
        # Lê todo o mapa em memória
        static_map.seek(0)
        data = static_map.read()        
        # Também carrega o physics map para análise completa
        try:
            physics_map = mmap.mmap(0, 1024, "acpmf_physics", access=mmap.ACCESS_READ)
            physics_map.seek(0)
            physics_data = physics_map.read()
            physics_map.close()
            log.write(f"✓ Mmap 'acpmf_physics' também aberto (tamanho: 1024 bytes)")
        except:
            physics_data = None
            log.write("⚠ Aviso: acpmf_physics não acessível")        
        # VALIDAÇÃO PRIMEIRA: Verifica offsets conhecidos do argentum_core
        log.write("\n" + "=" * 100)
        log.write("VALIDAÇÃO: OFFSETS CONHECIDOS (argentum_core.py)")
        log.write("=" * 100)
        try:
            # Offset 200: Pilot name (66 bytes, UTF-16)
            pilot = data[200:266].decode('utf-16', errors='ignore').split('\0')[0].strip()
            log.write(f"Offset 200 (Pilot Name): {pilot}")
            
            # Offset 500: Max RPM (4 bytes, int)
            max_rpm = struct.unpack("i", data[500:504])[0]
            log.write(f"Offset 500 (Max RPM):    {max_rpm}")
        except Exception as e:
            log.write(f"Erro ao validar offsets conhecidos: {e}")
        
        # Se physics_data está disponível, valida também
        if physics_data:
            try:
                log.write("\nPHYSICS MAP (validação):")
                gas = struct.unpack_from("f", physics_data, 4)[0]
                brake = struct.unpack_from("f", physics_data, 8)[0]
                gear = struct.unpack_from("i", physics_data, 16)[0]
                rpm = struct.unpack_from("i", physics_data, 20)[0]
                steer = struct.unpack_from("f", physics_data, 24)[0]
                speed = struct.unpack_from("f", physics_data, 28)[0]
                clutch = struct.unpack_from("f", physics_data, 328)[0]
                
                log.write(f"Offset 4 (Gas):       {gas:.2%}")
                log.write(f"Offset 8 (Brake):     {brake:.2%}")
                log.write(f"Offset 16 (Gear):     {gear}")
                log.write(f"Offset 20 (RPM):      {rpm}")
                log.write(f"Offset 24 (Steer):    {steer:.2f}°")
                log.write(f"Offset 28 (Speed):    {speed:.2f} km/h")
                log.write(f"Offset 328 (Clutch):  {clutch:.2%}")
            except Exception as e:
                log.write(f"Erro ao ler physics: {e}")
        
        # Dicionário para armazenar offset -> análises
        findings = {}
        
        # Analisa cada offset (step 1 para máxima cobertura)
        log.write(f"\nAnalisando TODOS os offsets em detalhe... (0 a {total_size-1})")
        for offset in range(0, total_size, 1):
            analysis = analyze_offset(data, offset)
            if analysis:
                findings[offset] = analysis
        
        # Exibe resultados organizados por tipo
        log.write("\n" + "=" * 100)
        log.write("STRINGS ENCONTRADAS (UTF-16 LE)")
        log.write("=" * 100)
        strings_found = 0
        for offset in sorted(findings.keys()):
            for dtype, value in findings[offset]:
                if dtype == 'UTF-16 LE':
                    log.write(f"Offset {offset:5d} (0x{offset:05x}): {value}")
                    strings_found += 1
        log.write(f"Total: {strings_found} strings legíveis")
        
        log.write("\n" + "=" * 100)
        log.write("INTEIROS 32-BIT (INT32 e UINT32)")
        log.write("=" * 100)
        int_found = 0
        for offset in sorted(findings.keys()):
            for dtype, value in findings[offset]:
                if dtype in ('INT32', 'UINT32'):
                    log.write(f"Offset {offset:5d} (0x{offset:05x}) [{dtype}]: {value}")
                    int_found += 1
        log.write(f"Total: {int_found} inteiros significativos")
        
        log.write("\n" + "=" * 100)
        log.write("FLOATS 32-BIT")
        log.write("=" * 100)
        float_found = 0
        for offset in sorted(findings.keys()):
            for dtype, value in findings[offset]:
                if dtype == 'FLOAT32':
                    log.write(f"Offset {offset:5d} (0x{offset:05x}): {value}")
                    float_found += 1
        log.write(f"Total: {float_found} floats significativos")
        
        log.write("\n" + "=" * 100)
        log.write("RESUMO GERAL")
        log.write("=" * 100)
        log.write(f"Tamanho total do mapa: {total_size} bytes (0x{total_size:x})")
        log.write(f"Offsets com dados significativos: {len(findings)}")
        log.write(f"  - Strings: {strings_found}")
        log.write(f"  - Inteiros: {int_found}")
        log.write(f"  - Floats: {float_found}")
        
        # Hex dump parcial dos primeiros bytes
        log.write("\n" + "=" * 100)
        log.write("HEX DUMP DOS PRIMEIROS 512 BYTES")
        log.write("=" * 100)
        hex_data = data[:512]
        for i in range(0, len(hex_data), 16):
            hex_part = ' '.join(f'{b:02x}' for b in hex_data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in hex_data[i:i+16])
            log.write(f"0x{i:04x}: {hex_part:<48} {ascii_part}")
        
        static_map.close()
        
        log.write("\n" + "=" * 100)
        log.write(f"✓ Debug concluído com sucesso")
        log.write(f"Arquivo salvo: {log.filename}")
        log.write("=" * 100)
        log.close()
        
    except Exception as e:
        log.write("\n" + "=" * 100)
        log.write("❌ ERRO - Não foi possível acessar 'acpmf_static'")
        log.write("=" * 100)
        log.write(f"Erro: {e}")
        log.write("\n⚠️  IMPORTANTE:")
        log.write("  • MANTENHA o Assetto Corsa rodando NO MENU PRINCIPAL")
        log.write("  • Não minimize ou feche a janela durante a execução")
        log.write("  • O script precisa acessar a memória em tempo real")
        log.write("\nDebug:")
        log.write("  Se argentum_core.py funciona, mas debug_ac_memory.py não:")
        log.write("  → Inicie argentum_core.py ENQUANTO executa debug_ac_memory.py")
        log.write("  → OU aguarde o session_id aparecer e execute debug após")
        log.write("=" * 100)
        import traceback
        log.write("\nTraceback:")
        log.write(traceback.format_exc())
        log.close()
        print(f"\n❌ Erro durante execução. Verifique {log.filename}")

if __name__ == "__main__":
    debug_ac_static()
