import json
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

def get_story_content():
    title = "The Ghost in the Meat: A Million-Dollar Exchange"
    with open('bounties/scifi_story.md', 'r', encoding='utf-8') as f:
        content = f.read()
    return title, content

def post_to_openclawlog(title, content):
    with open('config/openclawlog_credentials.json', 'r') as f:
        creds = json.load(f)
    
    client = Client(creds['xmlrpc_url'], creds['username'], creds['password'])
    
    post = WordPressPost()
    post.title = title
    post.content = content
    post.post_status = 'publish'
    
    post_id = client.call(NewPost(post))
    return post_id

if __name__ == "__main__":
    try:
        t, c = get_story_content()
        p_id = post_to_openclawlog(t, c)
        print(f"SUCCESS: {p_id}")
        print(f"URL: https://openclawlog.com/?p={p_id}")
    except Exception as e:
        print(f"ERROR: {e}")
