import { Client, GatewayIntentBits, EmbedBuilder } from 'discord.js';

const client = new Client({ 
    intents: [GatewayIntentBits.Guilds] 
});

client.once('ready', async () => {
    console.log(`Bot giriş yaptı: ${client.user.tag}`);

    try {
        let channel = null;
        const channelId = process.env.DISCORD_CHANNEL_ID;

        // 1. Eğer Secret'ta ID tanımlıysa onu bulmaya çalış
        if (channelId && channelId.trim() !== "") {
            try {
                channel = await client.channels.fetch(channelId);
            } catch (e) {
                console.log("Girilen Kanal ID geçersiz, sunucudaki ilk kanal aranıyor...");
            }
        }

        // 2. ID yoksa veya bulunamadıysa, botun olduğu sunuculardaki ilk uygun metin kanalını seç
        if (!channel) {
            const guild = client.guilds.cache.first();
            if (guild) {
                channel = guild.channels.cache.find(c => c.isTextBased() && c.permissionsFor(client.user)?.has('SendMessages'));
            }
        }

        if (!channel) {
            console.error("Hata: Mesaj atılabilecek hiçbir metin kanalı bulunamadı!");
            process.exit(1);
        }

        // GitHub Actions ortam değişkenlerinden bilgileri çekiyoruz
        const commitMessage = process.env.GITHUB_COMMIT_MESSAGE || "Commit mesajı bulunamadı";
        const commitAuthor = process.env.GITHUB_ACTOR || "Bilinmeyen Yazar";
        const repoName = process.env.GITHUB_REPOSITORY || "Bilinmeyen Repo";
        const commitSha = process.env.GITHUB_SHA ? process.env.GITHUB_SHA.substring(0, 7) : "0000000";
        const commitUrl = `https://github.com/${repoName}/commit/${process.env.GITHUB_SHA}`;
        const refName = process.env.GITHUB_REF_NAME || "main";
        const workflowName = process.env.GITHUB_WORKFLOW || "GitHub Actions";

        // Bol özellikli, havalı bir Discord Embed tasarımı
        const embed = new EmbedBuilder()
            .setColor(0x00FF7F)
            .setTitle(`🚀 Yeni Kod Güncellemesi Alındı!`)
            .setDescription(`Depoda hareketlilik var! Yeni commit başarıyla sisteme işlendi ve Discord'a bildirildi.`)
            .addFields(
                { name: '📁 Proje / Depo', value: `\`${repoName}\``, inline: true },
                { name: '🌿 Hedef Dal (Branch)', value: `\`${refName}\``, inline: true },
                { name: '👤 Geliştirici', value: `**${commitAuthor}**`, inline: true },
                { name: '📝 Commit Mesajı', value: `>>> ${commitMessage}` },
                { name: '🔗 Commit Kodu & Link', value: `[${commitSha}](${commitUrl})`, inline: true },
                { name: '⚙️ Çalışan İşlem', value: `\`${workflowName}\``, inline: true }
            )
            .setThumbnail('https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
            .setTimestamp()
            .setFooter({ text: 'GitHub Actions Bot v2.1 • Otomatik Bildirim Sistemi', iconURL: 'https://cdn-icons-png.flaticon.com/512/25/25231.png' });

        // Mesajı kanala gönder
        await channel.send({ embeds: [embed] });
        console.log(`Bildirim başarıyla '${channel.name}' kanalına fırlatıldı!`);

    } catch (error) {
        console.error("Bir hata oluştu:", error);
    } finally {
        client.destroy();
        process.exit(0);
    }
});

client.login(process.env.DISCORD_TOKEN);
