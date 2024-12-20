import logging

from pycheatengine.utils.logging_config import setup_logging

setup_logging()

from pycheatengine.bots.farming_bot import FarmingBot

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('Bot started')
    bot = FarmingBot(
        'MSI App Player',
        {
            'ad_gems': r'C:\Users\mikul\Pictures\Screenshots\ad_gems.png',
            'floating_gem': r'C:\Users\mikul\Pictures\Screenshots\floating_gem.png'
        })
    bot.start()