import random
import time
import threading
from playwright.sync_api import sync_playwright

# Number of browsers to run simultaneously
browsers_count = 2

# Control flag for continuous running
running = True

def generate_random_ua():
    """Generate a realistic-looking Android User-Agent with randomized components"""
    
    # Only Android mobile templates
    templates = [
        "Mozilla/{mozilla_ver} (Linux; Android {android_ver}; {device}) AppleWebKit/{webkit_ver} (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/{safari_ver}",
        "Mozilla/{mozilla_ver} (Linux; Android {android_ver}; {device}) AppleWebKit/{webkit_ver} (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/{safari_ver}",
    ]
    
    # Android devices only
    devices = [
        "Pixel 7", "Pixel 6", "Pixel 8", "SM-G998B", "SM-S908B", 
        "SM-A536B", "OnePlus 9", "OnePlus 10", "OnePlus 11",
        "Redmi Note 12", "Mi 13", "CPH2451", "VOG-L29",
        "Nexus 5", "Nexus 6P", "Pixel 4a", "Pixel 5",
        "SM-G991B", "SM-G996B", "Pixel 7 Pro", "Pixel 8 Pro"
    ]
    
    def random_mozilla_ver():
        """Mozilla version between 4.0 and 5.9"""
        major = random.randint(4, 5)
        minor = random.randint(0, 9)
        return f"{major}.{minor}"
    
    def random_android_ver():
        return str(random.randint(10, 15))
    
    def random_webkit_ver():
        return f"{random.randint(600, 620)}.{random.randint(1, 99)}"
    
    def random_chrome_ver():
        major = random.randint(100, 125)
        minor = random.randint(0, 9)
        build = random.randint(4000, 9999)
        patch = random.randint(1, 999)
        return f"{major}.{minor}.{build}.{patch}"
    
    def random_safari_ver():
        return f"{random.randint(600, 620)}.{random.randint(1, 99)}"
    
    template = random.choice(templates)
    
    ua = template.format(
        mozilla_ver=random_mozilla_ver(),
        android_ver=random_android_ver(),
        device=random.choice(devices),
        webkit_ver=random_webkit_ver(),
        chrome_ver=random_chrome_ver(),
        safari_ver=random_safari_ver(),
    )
    
    return ua

def get_random_referrer():
    """Return one of 3 referrer URLs"""
    referrers = [
        "https://www.google.com/",
        "https://www.facebook.com/",
        "https://www.youtube.com/",
    ]
    
    return random.choice(referrers)

def browser_worker(worker_id):
    """Continuous worker that opens browser, loads page, closes, and repeats"""
    
    cycle = 0
    
    while running:
        cycle += 1
        user_agent = generate_random_ua()
        referrer = get_random_referrer()
        
        # OnePlus 11 viewport
        viewport = {"width": 412, "height": 914}
        
        print(f"\n[Worker {worker_id}] Cycle {cycle} - Opening browser...")
        print(f"[Worker {worker_id}] UA: {user_agent[:80]}...")
        print(f"[Worker {worker_id}] Referrer: {referrer}")
        
        try:
            with sync_playwright() as p:
                # Launch browser for Android mobile
                browser = p.chromium.launch(
                    headless=False,
                    proxy={
                        "server": "http://127.0.0.1:3000"
                    },
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials',
                    ]
                )
                
                # Create context with OnePlus 11 settings
                context = browser.new_context(
                    user_agent=user_agent,
                    viewport=viewport,
                    is_mobile=True,
                    has_touch=True,
                    device_scale_factor=2.75,
                    java_script_enabled=True,
                    bypass_csp=True,
                    ignore_https_errors=True,
                )
                
                # Set minimal headers
                context.set_extra_http_headers({
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                })
                
                # Create page
                page = context.new_page()
                
                # Navigate - wait for DOM content loaded only
                start_time = time.time()
                
                page.goto(
                    "https://ptpss.online/v.php?user=6842", 
                    wait_until="domcontentloaded",
                    timeout=30000,
                    referer=referrer
                )
                
                load_time = time.time() - start_time
                
                # Quick check
                title = page.title()
                
                print(f"[Worker {worker_id}] Cycle {cycle} ✅ Loaded! ({load_time:.2f}s) - Title: {title}")
                
                # Close immediately
                context.close()
                browser.close()
                print(f"[Worker {worker_id}] Cycle {cycle} ✅ Closed!")
                
        except Exception as e:
            print(f"[Worker {worker_id}] Cycle {cycle} ❌ Error: {str(e)[:100]}")
        
        # Small delay before next cycle
        time.sleep(random.uniform(1, 3))

def main():
    print(f"\n{'='*60}")
    print(f"Starting {browsers_count} continuous browser workers")
    print(f"Each worker opens/closes browsers repeatedly")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    # Create and start worker threads
    threads = []
    for i in range(1, browsers_count + 1):
        thread = threading.Thread(
            target=browser_worker,
            args=(i,),
            name=f"Worker-{i}",
            daemon=True
        )
        threads.append(thread)
        thread.start()
        print(f"[Main] Started worker {i}")
        time.sleep(0.5)
    
    print(f"\n[Main] {browsers_count} workers running. Press Ctrl+C to stop...\n")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        global running
        running = False
        print(f"\n\n[Main] Stopping all workers...")
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=5)
        
        print(f"[Main] ✅ All workers stopped!")

if __name__ == "__main__":
    print("OnePlus 11 Mobile Emulator - Continuous Browser Workers")
    print(f"Workers: {browsers_count} (simultaneous)")
    print(f"Each worker: opens browser → loads DOM → closes → repeats")
    print(f"Wait strategy: domcontentloaded (close immediately)")
    print(f"Referrers: Google, Facebook, YouTube")
    print(f"Mozilla version range: 4.0 - 5.9")
    print("="*60)
    
    main()
