import { Client, GatewayIntentBits, EmbedBuilder } from 'discord.js';

const client = new Client({ 
    intents: [GatewayIntentBits.Guilds] 
});

client.once('ready', async () => {
    console.log(`Bot giriş yaptı: ${client.user.tag}`);

    try {
        const channelId = process.env.DISCORD_CHANNEL_ID;
        const channel = await client.channels.fetch(channelId);

        if (!channel) {
            console.error("Kanal bulunamadı!");
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
            .setColor(0x00FF7F) // Canlı bir yeşil renk
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
            .setFooter({ text: 'GitHub Actions Bot v2.0 • Otomatik Bildirim Sistemi', iconURL: 'https://cdn-icons-png.flaticon.com/512/25/25231.png' });

        // Mesajı kanala çak
        await channel.send({ embeds: [embed] });
        console.log("Bildirim Discord'a başarıyla fırlatıldı!");

    } catch (error) {
        console.error("Bir hata oluştu:", error);
    } finally {
        client.destroy();
        process.exit(0);
    }
});

// Senin secrets'ta tanımladığın DISCORD_TOKEN'ı buraya direkt bağladık
client.login(process.env.DISCORD_TOKEN);
