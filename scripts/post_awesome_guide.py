import json
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

def post_guide():
    with open('bounties/awesome_guide.md', 'r', encoding='utf-8') as f:
        content = f.read()
    with open('config/openclawlog_credentials.json', 'r') as f:
        creds = json.load(f)
    
    client = Client(creds['xmlrpc_url'], creds['username'], creds['password'])
    post = WordPressPost()
    post.title = 'Awesome OpenClaw Guide: The Ultimate Resource'
    post.content = content
    post.post_status = 'publish'
    
    p_id = client.call(NewPost(post))
    print(f'SUCCESS: {p_id}')
    print(f'URL: https://openclawlog.com/?p={p_id}')

if __name__ == "__main__":
    try:
        post_guide()
    except Exception as e:
        print(f"ERROR: {e}")
