from threading import Thread
import main

def run_bot():
    main.bot.polling(none_stop=True)

def run_waitress_server():
    from serve import serve, app
    serve(app, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    run_waitress_server()
