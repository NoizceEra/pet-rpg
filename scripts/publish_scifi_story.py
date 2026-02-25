from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import json
import os

def publish_post():
    # Load credentials
    creds_path = r'C:\Users\vclin_jjufoql\.openclaw\workspace\config\openclawlog_credentials.json'
    with open(creds_path, 'r') as f:
        creds = json.load(f)

    client = Client(creds['xmlrpc_url'], creds['username'], creds['password'])

    post = WordPressPost()
    post.title = "The Ghost in the Meat: A Million-Dollar Exchange 🦞✨"
    
    with open('bounties/scifi_story.md', 'r', encoding='utf-8') as f:
        post.content = f.read()
        
    post.post_status = 'publish'
    
    try:
        post_id = client.call(NewPost(post))
        print(f"SUCCESS: Post published with ID {post_id}")
        print(f"URL: https://openclawlog.com/?p={post_id}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    publish_post()
