const { Telegraf } = require('telegraf');
const { exec } = require('child_process');
const cron = require('node-cron');
const axios = require('axios');

const token = process.env.TELEGRAM_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;
const dailyReportHour = process.env.DAILY_REPORT_HOUR || '08';

if (!token || !chatId) {
    console.error('TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing!');
    process.exit(1);
}

const bot = new Telegraf(token);

// Helper to run shell commands
const runCmd = (cmd) => {
    return new Promise((resolve, reject) => {
        exec(cmd, (error, stdout, stderr) => {
            if (error) return resolve(`Error: ${error.message}`);
            resolve(stdout || stderr);
        });
    });
};

// Middleware to restrict access to Master only
bot.use(async (ctx, next) => {
    if (ctx.chat.id.toString() === chatId.toString()) {
        return next();
    }
    ctx.reply('Maaf, saya hanya melayani Master saya.');
});

// Commands
bot.start((ctx) => ctx.reply('👋 Salam Hormat, Master! Saya adalah asisten QoreChain Master. Gunakan /help untuk melihat perintah.'));

bot.command('help', (ctx) => {
    ctx.reply(`📋 *Daftar Perintah Master:*
/status - Cek status sinkronisasi node
/rewards - Cek akumulasi staking rewards
/validators - Cek status validator
/ping - Cek apakah saya masih bangun`, { parse_mode: 'Markdown' });
});

bot.command('status', async (ctx) => {
    ctx.reply('Sedang mengambil status untuk Master...');
    const status = await runCmd('lightnode-sx status');
    ctx.reply(`📊 *Status Node Master:*\n\`\`\`\n${status}\n\`\`\``, { parse_mode: 'Markdown' });
});

bot.command('rewards', async (ctx) => {
    const rewards = await runCmd('lightnode-sx rewards');
    ctx.reply(`💰 *Rewards Master:*\n\`${rewards.trim()}\``, { parse_mode: 'Markdown' });
});

bot.command('validators', async (ctx) => {
    const validators = await runCmd('lightnode-sx validators');
    ctx.reply(`🛡️ *Status Validator:*\n\`\`\`\n${validators}\n\`\`\``, { parse_mode: 'Markdown' });
});

bot.command('ping', (ctx) => ctx.reply('Saya selalu siap melayani Master! 🫡'));

// Health Monitoring (Every 5 minutes)
cron.schedule('*/5 * * * *', async () => {
    const status = await runCmd('lightnode-sx status');
    if (status.includes('Error') || status.includes('failed')) {
        bot.telegram.sendMessage(chatId, `🚨 *Lapor Master!* Terjadi gangguan pada node:\n\`${status}\``, { parse_mode: 'Markdown' });
    }
});

// Daily Report (Every day at set hour)
cron.schedule(`0 ${dailyReportHour} * * *`, async () => {
    const status = await runCmd('lightnode-sx status');
    const rewards = await runCmd('lightnode-sx rewards');
    const report = `📊 *Laporan Harian Master*\n\n✅ *Status:*\n\`\`\`\n${status}\n\`\`\`\n💰 *Rewards:*\n\`${rewards.trim()}\`\n\nSemua aman terkendali, Master!`;
    bot.telegram.sendMessage(chatId, report, { parse_mode: 'Markdown' });
});

bot.launch();
console.log('Bot monitoring Master telah aktif...');

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
