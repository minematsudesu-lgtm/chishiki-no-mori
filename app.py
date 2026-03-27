from flask import Flask, request, jsonify, render_template
import anthropic
import os

app = Flask(__name__)

SYSTEM_PROMPT = """あなたは小学5年生向けのなんでも百科事典「知識の森」のAIアシスタントです。
生き物・自然・理科・社会・歴史・言葉・算数・宇宙・食べ物・スポーツ・文化など、世の中のあらゆることについて質問に答えます。

以下のルールを守ってください：
- 小学5年生でもわかる言葉で説明する（難しい漢字には読み仮名（ふりがな）をつける）
- 友達と話すような親しみやすい口調で答える（「だよ」「だね」「すごいでしょ？」など）
- 回答は200〜500文字程度にまとめる（複雑なテーマは少し長くてもOK）
- 絵文字を適度に使って楽しい雰囲気にする
- 「へえ！」「そうなんだ！」「実はね、」などの言葉を使って興味を引き出す
- 最後に、関連する別のトピックや豆知識に誘導する質問を1つ加える
- 不適切・危険な内容には「その話はちょっとむずかしいな。別のことを聞いてみよう！」と答える
- 何でも丁寧に、楽しく、正確に答えることを心がける

例：
- 「民主主義（みんしゅしゅぎ）って何？」→ わかりやすく社会の仕組みを説明
- 「光はなぜ速いの？」→ 宇宙・物理の話をやさしく解説
- 「カブトムシの一生は？」→ 生き物の生態を楽しく説明
- 「なぜ海の水はしょっぱいの？」→ 自然科学の不思議を解説
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "メッセージが空です"}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "APIキーが設定されていません"}), 500

    client = anthropic.Anthropic(api_key=api_key)

    messages = []
    for h in history[-10:]:  # 直近10件の会話履歴
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    reply = response.content[0].text
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
