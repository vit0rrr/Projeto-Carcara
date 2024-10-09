import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob

app = Flask(__name__)
CORS(app)


@app.route('/analyze', methods=['GET'])
def analyze_posts():
    query = request.args.get('q', default='', type=str)
    limit = request.args.get('limit', default=10, type=int)

    if not query:
        return jsonify({'error': 'Parâmetro de busca (q) é obrigatório.'}), 400

    base_url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {
        'q': query,
        'sort': 'latest',
        'limit': limit,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        analyzed_posts = []

        for post in data.get('posts', []):
            author_name = post.get('author', {}).get('displayName', 'Autor desconhecido')
            post_text = post.get('record', {}).get('text', 'Texto indisponível')

            blob = TextBlob(post_text)
            sentimento = blob.sentiment.polarity

            if sentimento > 0:
                sentimento_texto = "Positivo"
            elif sentimento < 0:
                sentimento_texto = "Negativo"
            else:
                sentimento_texto = "Neutro"

            analyzed_posts.append({
                'author': author_name,
                'post_text': post_text,
                'sentimento': sentimento_texto
            })

        return jsonify(analyzed_posts), 200
    else:
        return jsonify(
            {'error': f"Erro ao acessar API: {response.status_code} - {response.text}"}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
