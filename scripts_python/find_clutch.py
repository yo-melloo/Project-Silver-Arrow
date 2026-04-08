"""
Tentativa de localizar o offset de embreagem
STATUS: Encontrado em 364
Nota: A embreagem funciona reverso a lógica de aceleração e freio, então abertar o botão de embreagem na verdade solta a embreagem.
"""

import mmap, struct, time

try:
    p = mmap.mmap(0, 1024, "acpmf_physics", access=mmap.ACCESS_READ)
    print("BOMBEIE A EMBREAGEM AGORA! (solte e aperte várias vezes) Lendo por 5 seg...")
    
    start = time.time()
    mins = {}
    maxs = {}
    for i in range(0, 1024, 4):
        mins[i] = 1000.0
        maxs[i] = -1000.0
        
    while time.time() - start < 5:
        for i in range(0, 1024, 4):
            try:
                v = struct.unpack('f', p[i:i+4])[0]
                if v < mins[i]: mins[i] = v
                if v > maxs[i]: maxs[i] = v
            except:
                pass
                
    found = False
    for i in range(0, 1024, 4):
        diff = maxs[i] - mins[i]
        # Clutch, gas and brake usually go from 0.0 to 1.0 (diff ~1.0)
        if 0.4 < diff < 1.2 and mins[i] >= 0.0 and maxs[i] <= 1.1:
            print(f"ENCONTRADO -> Offset {i}: varia de {mins[i]:.2f} a {maxs[i]:.2f}")
            found = True
            
    if not found:
        print("Nenhuma variação entre 0.0 e 1.0 encontrada!")
        
except Exception as e:
    print(f"Erro: {e}")
