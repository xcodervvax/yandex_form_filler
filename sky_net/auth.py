from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path="/usr/bin/google-chrome"
    )
    
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://a.intimstory.bet/sky_net/")
    
    print("👉 Войди в аккаунт вручную, затем нажми ENTER")
    input()
    
    # Сохраняем сессию
    context.storage_state(path="auth.json")
    
    print("✅ Сессия сохранена")
    browser.close()