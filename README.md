# windows-time-sync

so I dual boot Ubuntu and Windows on my laptop and every time I log into Windows the clock is wrong. turns out Ubuntu stores the hardware clock in UTC but Windows expects local time — they basically disagree on how to read the clock.

the usual fix is going into date & time settings and hitting the sync  button manually. got tired of doing that every single time so I wrote this script to handle it automatically on login.

---

## what's in here

- `sync_time.py` — the script that does the actual syncing
- `run_sync_time.bat` — runs the script silently so no console window flashes on login

---

## what you need

- Python installed on Windows — grab it from [python.org](https://www.python.org/downloads/) if you don't have it
- that's pretty much it, the admin part is handled through Task Scheduler

---

## how to set it up

**1. drop both files somewhere**

like `C:\Scripts\` or your Desktop, doesn't matter. just keep them in the same folder.

**2. open Task Scheduler**

search for it in the Start menu, then click **Create Task** (not the Basic Task one)

**3. General tab**

- name it whatever, I used `Sync Time on Login`
- check **Run with highest privileges** — important, won't work without this
- set *Configure for* to **Windows 10** (works fine on Windows 11 too)

**4. Triggers tab**

- New → **At log on** → Any user → OK

**5. Actions tab**

- New → Start a program → point it to `run_sync_time.bat`
- example: `C:\Scripts\run_sync_time.bat`

**6. Conditions tab**

- uncheck **Start only if on AC power** otherwise it won't run when you're on battery

**7. hit OK and you're done**

next time you log in, the clock will sync on its own.

---

## log file

the script creates a `sync_time.log` in the same folder. if something seems off, check that first.

---

## permanent fix (optional)

if you'd rather fix this properly on the Ubuntu side instead, just run this once in your terminal:

```bash
timedatectl set-local-rtc 1 --adjust-system-clock
```

that makes Ubuntu use local time for the hardware clock just like Windows does, and the mismatch is gone for good. I just preferred handling it on the Windows side.
