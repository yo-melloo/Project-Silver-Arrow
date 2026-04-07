import mmap
import struct
import time

print("🔍 PROCURANDO PELO TEMPO DE SESSÃO (45 MINUTOS = 2700 SEGUNDOS)\n")
print("Testando TODOS os offsets (0-1024)...")
print("=" * 90)

try:
    physics_map = mmap.mmap(0, 1024, "acpmf_physics", access=mmap.ACCESS_READ)
    
    candidates = []
    
    # Testando como FLOATS
    print("\n📊 TESTANDO COMO FLOATS:\n")
    for offset in range(0, 1024, 4):
        try:
            physics_map.seek(offset)
            value = struct.unpack("f", physics_map.read(4))[0]
            
            # 45 minutos = 2700 segundos
            # Procurando valores próximos (entre 2650 e 2750)
            if 2650 <= value <= 2750:
                print(f"✓✓✓ Offset {offset:3d}: {value:12.2f}s (≈ {value/60:.1f} min) <- POSSÍVEL!")
                candidates.append(("float", offset, value))
            # Também procurar em outras escalas próximas
            elif 2.65 <= value <= 2.75:  # Se estiver em unidades de minutos
                print(f"✓✓✓ Offset {offset:3d}: {value:12.2f} (≈ {value*60:.1f}s se for em minutos?)")
                candidates.append(("float", offset, value))
        except:
            pass
    
    # Testando como INTS
    print("\n📊 TESTANDO COMO INTS (32-bit):\n")
    for offset in range(0, 1024, 4):
        try:
            physics_map.seek(offset)
            value = struct.unpack("i", physics_map.read(4))[0]
            
            # Procurando 2700 ou variações
            if value == 2700:
                print(f"✓✓✓ Offset {offset:3d}: {value} (EXATO! 45 minutos em segundos)")
                candidates.append(("int", offset, value))
            # Procurar 270000 (si em centésimos de segundo)
            elif value == 270000:
                print(f"✓✓✓ Offset {offset:3d}: {value} (EXATO! 45 minutos em centésimos)")
                candidates.append(("int", offset, value))
            # Procurar em range (com margem)
            elif 2650 <= value <= 2750:
                print(f"✓✓✓ Offset {offset:3d}: {value} (≈ {value/60:.1f} min)")
                candidates.append(("int", offset, value))
            # Testar se é em centésimos (270000 ± 5000)
            elif 265000 <= value <= 275000:
                seconds_from_centesimos = value / 100
                print(f"✓✓✓ Offset {offset:3d}: {value} (= {seconds_from_centesimos:.0f}s ≈ {seconds_from_centesimos/60:.1f} min, se centésimos)")
                candidates.append(("int_centesimos", offset, value))
        except:
            pass
    
    # Testando como UNSIGNED INTS também
    print("\n📊 TESTANDO COMO UNSIGNED INTS (32-bit):\n")
    for offset in range(0, 1024, 4):
        try:
            physics_map.seek(offset)
            value = struct.unpack("I", physics_map.read(4))[0]
            
            if value == 2700:
                print(f"✓✓✓ Offset {offset:3d}: {value} (EXATO! 45 minutos em segundos)")
                candidates.append(("uint", offset, value))
            elif 265000 <= value <= 275000:
                seconds = value / 100
                print(f"✓✓✓ Offset {offset:3d}: {value} (= {seconds:.0f}s ≈ {seconds/60:.1f} min)")
                candidates.append(("uint_centesimos", offset, value))
        except:
            pass
    
    # Resumo
    print("\n" + "=" * 90)
    print(f"\n📋 RESUMO: Encontrados {len(candidates)} candidatos\n")
    for data_type, offset, value in candidates:
        print(f"   [{data_type:17s}] Offset {offset:3d}: {value}")
    
    physics_map.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n⚠️  Assetto Corsa precisa estar rodando COM sessão ativa de 45 min!")
