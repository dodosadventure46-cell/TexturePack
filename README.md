# PvP Smooth 32x Resource Pack

Resource pack Bedrock/MCPE 1.26.51.1 untuk pengaturan PvP dengan gaya "clean vanilla + smoother". Fokus utamanya adalah:

- texture tetap ada
- tampil lebih halus di 32x
- warna dan kontras lebih jelas untuk PvP
- tidak mengubah gameplay
- ringan untuk Android

## Struktur

```text
.
├── README.md
├── requirements.txt
├── build_pvp_smooth_32x.py
├── PvP_Smooth_32x/
│   ├── manifest.json
│   ├── pack_icon.png
│   ├── texts/
│   │   └── en_US.lang
│   └── textures/
│       ├── items/
│       └── ui/
├── PvP_Smooth_32x.mcpack
└── .gitignore
```

## Cara pakai

1. Install dependency:

```bash
pip install -r requirements.txt
```

2. Jalankan generator:

```bash
python build_pvp_smooth_32x.py
```

3. Hasil output akan dibuat otomatis di folder `PvP_Smooth_32x/` dan arsip `PvP_Smooth_32x.mcpack`.

4. Untuk Android / Bedrock:

- pindahkan `.mcpack` ke folder resource packs
- atau ekstrak folder `PvP_Smooth_32x` ke `games/com.mojang/resource_packs`
- masuk Minecraft > Setelan > Paket Sumber Daya > aktifkan pack

## Catatan performa

Pack ini dibuat dengan resolusi 32x agar:

- tetap cukup halus untuk PvP
- lebih ringan daripada 64x/128x
- cocok untuk ponsel Android yang tidak terlalu kuat

## Pengaturan default

- resolusi: 32x
- gaya: clean/minimal
- fokus: item PvP utama + UI hotbar + crosshair
- kompatibel: MCPE/Bedrock 1.26.x

## Export final

Setelah generator dijalankan, file `.mcpack` siap dipindahkan ke perangkat Android dan diubah jadi pack aktif di Minecraft.
