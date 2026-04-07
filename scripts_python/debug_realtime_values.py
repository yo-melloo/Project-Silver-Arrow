import mmap
import struct
import time
import os

print("🔍 MONITORAMENTO EM TEMPO REAL DO PHYSICS_MAP\n")
print("Mostrando valores que MUDAM a cada segundo")
print("(O tempo deve estar incrementando em um desses valores)\n")
print("=" * 100)

try:
    physics_map = mmap.mmap(0, 1024, "acpmf_physics", access=mmap.ACCESS_READ)
    
    # Primeira leitura
    print("\n📸 LEITURA 1 (t=0s):\n")
    values_1 = {}
    for offset in range(0, 1024, 4):
        try:
            physics_map.seek(offset)
            f_value = struct.unpack("f", physics_map.read(4))[0]
            physics_map.seek(offset)
            i_value = struct.unpack("i", physics_map.read(4))[0]
            values_1[offset] = {"float": f_value, "int": i_value}
            
            # Mostra valores que parecem "interessantes" (não muito grandes)
            if (-1000 <= f_value <= 10000 and f_value != 0):
                print(f"  Offset {offset:3d}: float={f_value:12.2f}  |  int={i_value:12d}")
        except:
            pass
    
    print("\n⏳ Aguardando 3 segundos...\n")
    time.sleep(3)
    
    # Segunda leitura
    print("📸 LEITURA 2 (t=3s):\n")
    values_2 = {}
    for offset in range(0, 1024, 4):
        try:
            physics_map.seek(offset)
            f_value = struct.unpack("f", physics_map.read(4))[0]
            physics_map.seek(offset)
            i_value = struct.unpack("i", physics_map.read(4))[0]
            values_2[offset] = {"float": f_value, "int": i_value}
        except:
            pass
    
    # Comparação
    print("\n" + "=" * 100)
    print("📊 VALORES QUE MUDARAM (Δ):\n")
    
    changes = []
    for offset in values_1.keys():
        f1 = values_1[offset]["float"]
        i1 = values_1[offset]["int"]
        f2 = values_2[offset]["float"]
        i2 = values_2[offset]["int"]
        
        f_delta = f2 - f1
        i_delta = i2 - i1
        
        # Mostrar apenas mudanças interessantes
        if abs(f_delta) > 0.01 or abs(i_delta) > 0:
            changes.append({
                "offset": offset,
                "float_before": f1,
                "float_after": f2,
                "float_delta": f_delta,
                "int_before": i1,
                "int_after": i2,
                "int_delta": i_delta
            })
    
    # Ordena por maior mudança
    changes.sort(key=lambda x: abs(x["float_delta"]) + abs(x["int_delta"]), reverse=True)
    
    for change in changes:
        offset = change["offset"]
        print(f"\nOffset {offset:3d}:")
        print(f"  Float: {change['float_before']:12.2f} → {change['float_after']:12.2f}  (Δ = {change['float_delta']:+.2f})")
        print(f"  Int:   {change['int_before']:12d} → {change['int_after']:12d}  (Δ = {change['int_delta']:+d})")
        
        # Se incrementou ~3, provavelmente é o tempo em segundos
        if 2.9 <= abs(change["int_delta"]) <= 3.1:
            print(f"  ✓✓✓ MUITO PROVÁVEL SER O TEMPO! (incrementou ~3 em 3 segundos)")
    
    print("\n" + "=" * 100)
    print("\n💡 DICA: Procure por valores que incrementam aproximadamente 3 (para 3 segundos)")
    print("   Se encontrar um que incrementa ~1 a cada segundo, esse é o tempo da sessão!")
    
    physics_map.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n⚠️  Assetto Corsa precisa estar rodando COM sessão ativa!")
