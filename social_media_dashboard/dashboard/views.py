from django.shortcuts import render, redirect
import requests
import json
import os
import datetime
from collections import Counter
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
import tweepy

# Replace these with your actual Facebook app details from developers.facebook.com
FACEBOOK_APP_ID = 'YOUR_FACEBOOK_APP_ID'
FACEBOOK_APP_SECRET = 'YOUR_FACEBOOK_APP_SECRET'
FACEBOOK_ACCESS_TOKEN = 'YOUR_FACEBOOK_ACCESS_TOKEN'

# Replace these with your actual Twitter app details from developer.twitter.com
TWITTER_API_KEY = 'YOUR_TWITTER_API_KEY'
TWITTER_API_SECRET = 'YOUR_TWITTER_API_SECRET'
TWITTER_ACCESS_TOKEN = 'YOUR_TWITTER_ACCESS_TOKEN'
TWITTER_ACCESS_SECRET = 'YOUR_TWITTER_ACCESS_SECRET'

# JSON files where we save the API keys that users enter
FACEBOOK_CREDENTIALS_FILE = 'facebook_credentials.json'
TWITTER_CREDENTIALS_FILE = 'twitter_credentials.json'

def load_facebook_credentials():
    """Load Facebook API credentials from file if available"""
    global FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_ACCESS_TOKEN
    try:
        if os.path.exists(FACEBOOK_CREDENTIALS_FILE):
            with open(FACEBOOK_CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
                FACEBOOK_APP_ID = credentials.get('app_id', FACEBOOK_APP_ID)
                FACEBOOK_APP_SECRET = credentials.get('app_secret', FACEBOOK_APP_SECRET)
                FACEBOOK_ACCESS_TOKEN = credentials.get('access_token', FACEBOOK_ACCESS_TOKEN)
    except Exception as e:
        print(f"Error loading Facebook credentials: {e}")

def load_twitter_credentials():
    """Load Twitter API credentials from file if available"""
    global TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    try:
        if os.path.exists(TWITTER_CREDENTIALS_FILE):
            with open(TWITTER_CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
                TWITTER_API_KEY = credentials.get('api_key', TWITTER_API_KEY)
                TWITTER_API_SECRET = credentials.get('api_secret', TWITTER_API_SECRET)
                TWITTER_ACCESS_TOKEN = credentials.get('access_token', TWITTER_ACCESS_TOKEN)
                TWITTER_ACCESS_SECRET = credentials.get('access_secret', TWITTER_ACCESS_SECRET)
    except Exception as e:
        print(f"Error loading Twitter credentials: {e}")

# Load credentials on module import
load_facebook_credentials()
load_twitter_credentials()

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('platform_select')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('platform_select')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required
def platform_select_view(request):
    """View to select between Facebook and Twitter dashboards"""
    return render(request, 'dashboard/platform_select.html')

@login_required
def dashboard_view(request):
    """Main dashboard view showing Facebook profile information"""
    user_data = None
    posts_data = None
    error = None
    
    # Reload credentials in case they were updated
    load_facebook_credentials()
    
    # Check if we have real credentials or just placeholders
    if FACEBOOK_ACCESS_TOKEN == 'YOUR_FACEBOOK_ACCESS_TOKEN':
        return redirect('config')
    
    try:
        # Facebook Graph API endpoint for user profile
        api_url = f'https://graph.facebook.com/v19.0/me?fields=id,name,email,picture&access_token={FACEBOOK_ACCESS_TOKEN}'
        response = requests.get(api_url)
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Get user posts with reactions and comments - fixed API fields
            # Note: 'likes' field is replaced with 'reactions' which is the correct field name
            posts_url = f'https://graph.facebook.com/v19.0/me/posts?fields=id,message,created_time,reactions.summary(true),comments.summary(true).limit(5){{message,from}},attachments{{media,type,url}}&limit=10&access_token={FACEBOOK_ACCESS_TOKEN}'
            posts_response = requests.get(posts_url)
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json().get('data', [])
            else:
                error = f"Error fetching posts: {posts_response.json().get('error', {}).get('message', 'Unknown error')}"
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
    except Exception as e:
        error = str(e)
    
    return render(request, 'dashboard/dashboard.html', {
        'user_data': user_data, 
        'posts_data': posts_data,
        'error': error,
        'platform': 'facebook'
    })

@login_required
def config_view(request):
    """View for configuring Facebook API credentials"""
    message = None
    message_type = 'info'
    
    if request.method == 'POST':
        try:
            # Get credentials from form
            app_id = request.POST.get('app_id')
            app_secret = request.POST.get('app_secret')
            access_token = request.POST.get('access_token')
            
            # Save credentials to file
            credentials = {
                'app_id': app_id,
                'app_secret': app_secret,
                'access_token': access_token
            }
            
            with open(FACEBOOK_CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials, f)
            
            # Update global variables
            global FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_ACCESS_TOKEN
            FACEBOOK_APP_ID = app_id
            FACEBOOK_APP_SECRET = app_secret
            FACEBOOK_ACCESS_TOKEN = access_token
            
            message = "Configuration saved successfully!"
            message_type = "green"
            
            # Test the connection
            api_url = f'https://graph.facebook.com/v19.0/me?access_token={access_token}'
            response = requests.get(api_url)
            
            if response.status_code == 200:
                return redirect('dashboard')
            else:
                message = f"Configuration saved, but API test failed: {response.json().get('error', {}).get('message', 'Unknown error')}"
                message_type = "yellow"
                
        except Exception as e:
            message = f"Error saving configuration: {str(e)}"
            message_type = "red"
    
    return render(request, 'dashboard/config.html', {
        'message': message, 
        'message_type': message_type,
        'platform': 'facebook'
    })

@login_required
def twitter_config_view(request):
    """View for configuring Twitter API credentials"""
    message = None
    message_type = 'info'
    
    if request.method == 'POST':
        try:
            # Get credentials from form
            api_key = request.POST.get('api_key')
            api_secret = request.POST.get('api_secret')
            access_token = request.POST.get('access_token')
            access_secret = request.POST.get('access_secret')
            
            # Save credentials to file
            credentials = {
                'api_key': api_key,
                'api_secret': api_secret,
                'access_token': access_token,
                'access_secret': access_secret
            }
            
            with open(TWITTER_CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials, f)
            
            # Update global variables
            global TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
            TWITTER_API_KEY = api_key
            TWITTER_API_SECRET = api_secret
            TWITTER_ACCESS_TOKEN = access_token
            TWITTER_ACCESS_SECRET = access_secret
            
            # Also save to the user's profile
            if request.user.is_authenticated:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.twitter_api_key = api_key
                profile.twitter_api_secret = api_secret
                profile.twitter_access_token = access_token
                profile.twitter_access_secret = access_secret
                profile.save()
            
            message = "Twitter configuration saved successfully!"
            message_type = "green"
            
            # Test the connection
            try:
                auth = tweepy.OAuth1UserHandler(
                    api_key, api_secret,
                    access_token, access_secret
                )
                api = tweepy.API(auth)
                api.verify_credentials()
                return redirect('twitter_dashboard')
            except Exception as e:
                message = f"Configuration saved, but Twitter API test failed: {str(e)}"
                message_type = "yellow"
                
        except Exception as e:
            message = f"Error saving Twitter configuration: {str(e)}"
            message_type = "red"
    
    return render(request, 'dashboard/twitter_config.html', {
        'message': message, 
        'message_type': message_type,
        'platform': 'twitter'
    })

@login_required
def twitter_dashboard_view(request):
    """Main dashboard view showing Twitter profile information"""
    user_data = None
    tweets_data = None
    error = None
    
    # Reload credentials in case they were updated
    load_twitter_credentials()
    
    # Check if we have real credentials or just placeholders
    if TWITTER_API_KEY == 'YOUR_TWITTER_API_KEY':
        return redirect('twitter_config')
    
    try:
        # Set up Twitter API client
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, 
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, 
            TWITTER_ACCESS_SECRET
        )
        api = tweepy.API(auth)
        
        # Try to get profile information
        user_data = api.verify_credentials()._json
        
        # Try to get tweets
        tweets = api.user_timeline(count=10, tweet_mode='extended')
        tweets_data = [tweet._json for tweet in tweets]
        
    except Exception as e:
        error = f"Twitter API access restricted: {str(e)}"
        # Don't create sample data, just show the error
    
    return render(request, 'dashboard/twitter_dashboard.html', {
        'user_data': user_data, 
        'tweets_data': tweets_data,
        'error': error,
        'platform': 'twitter'
    })

@login_required
def twitter_analytics_view(request):
    """View for Twitter analytics dashboard"""
    # Reload credentials in case they were updated
    load_twitter_credentials()
    
    # Check if we have real credentials or just placeholders
    if TWITTER_API_KEY == 'YOUR_TWITTER_API_KEY':
        return redirect('twitter_config')
    
    user_data = None
    tweets_data = None
    error = None
    analytics_data = {
        'total_tweets': 0,
        'total_likes': 0,
        'total_retweets': 0,
        'avg_likes_per_tweet': 0,
        'avg_retweets_per_tweet': 0,
        'tweets_by_month': {},
        'engagement_by_month': {},
        'top_tweets': [],
        'tweet_types': {'text': 0, 'photo': 0, 'video': 0, 'link': 0, 'other': 0},
        'chart_labels': json.dumps([]),
        'chart_tweets_data': json.dumps([]),
        'chart_likes_data': json.dumps([]),
        'chart_retweets_data': json.dumps([]),
        'chart_post_types_labels': json.dumps(['Text', 'Photo', 'Video', 'Link', 'Other']),
        'chart_tweet_types_data': json.dumps([0, 0, 0, 0, 0])
    }
    
    try:
        # Set up Twitter API client
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, 
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, 
            TWITTER_ACCESS_SECRET
        )
        api = tweepy.API(auth)
        
        # Get user profile information - if this fails, the whole function will go to except
        user_data = api.verify_credentials()._json
        
        # Get tweets for analytics (up to 100 recent tweets)
        tweets = api.user_timeline(count=100, tweet_mode='extended')
        tweets_data = [tweet._json for tweet in tweets]
        
        # Process analytics data only if we have real tweets
        if tweets_data:
            analytics_data['total_tweets'] = len(tweets_data)
            total_likes = 0
            total_retweets = 0
            tweets_by_month = {}
            
            for tweet in tweets_data:
                # Count likes and retweets
                likes = tweet.get('favorite_count', 0)
                retweets = tweet.get('retweet_count', 0)
                total_likes += likes
                total_retweets += retweets
                
                # Determine tweet type
                if 'media' in tweet.get('entities', {}):
                    media_type = tweet['entities']['media'][0].get('type', 'photo')
                    if media_type == 'photo':
                        analytics_data['tweet_types']['photo'] += 1
                    elif media_type in ['video', 'animated_gif']:
                        analytics_data['tweet_types']['video'] += 1
                    else:
                        analytics_data['tweet_types']['other'] += 1
                elif 'urls' in tweet.get('entities', {}) and tweet['entities']['urls']:
                    analytics_data['tweet_types']['link'] += 1
                else:
                    analytics_data['tweet_types']['text'] += 1
                
                # Group by month
                created_at = datetime.datetime.strptime(
                    tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'
                )
                month_key = created_at.strftime('%Y-%m')
                month_name = created_at.strftime('%b %Y')
                
                if month_key not in tweets_by_month:
                    tweets_by_month[month_key] = {'name': month_name, 'count': 0, 'likes': 0, 'retweets': 0}
                
                tweets_by_month[month_key]['count'] += 1
                tweets_by_month[month_key]['likes'] += likes
                tweets_by_month[month_key]['retweets'] += retweets
            
            # Calculate averages
            if analytics_data['total_tweets'] > 0:
                analytics_data['total_likes'] = total_likes
                analytics_data['total_retweets'] = total_retweets
                analytics_data['avg_likes_per_tweet'] = round(total_likes / analytics_data['total_tweets'], 1)
                analytics_data['avg_retweets_per_tweet'] = round(total_retweets / analytics_data['total_tweets'], 1)
            
            # Sort tweets by engagement
            sorted_tweets = sorted(
                tweets_data, 
                key=lambda x: (x.get('favorite_count', 0) + x.get('retweet_count', 0)),
                reverse=True
            )
            
            # Get top 5 tweets
            analytics_data['top_tweets'] = sorted_tweets[:5]
            
            # Process tweets by month and prepare chart data
            chart_labels = []
            chart_tweets_data = []
            chart_likes_data = []
            chart_retweets_data = []
            
            for month_key, data in sorted(tweets_by_month.items()):
                analytics_data['tweets_by_month'][month_key] = data['count']
                engagement = data['likes'] + data['retweets']
                analytics_data['engagement_by_month'][month_key] = {
                    'name': data['name'],
                    'likes': data['likes'],
                    'retweets': data['retweets'],
                    'total': engagement
                }
                
                # Add data for charts
                chart_labels.append(data['name'])
                chart_tweets_data.append(data['count'])
                chart_likes_data.append(data['likes'])
                chart_retweets_data.append(data['retweets'])
            
            # Convert chart data to JSON for JavaScript
            analytics_data['chart_labels'] = json.dumps(chart_labels)
            analytics_data['chart_tweets_data'] = json.dumps(chart_tweets_data)
            analytics_data['chart_likes_data'] = json.dumps(chart_likes_data)
            analytics_data['chart_retweets_data'] = json.dumps(chart_retweets_data)
            
            # Add tweet types data for chart
            chart_tweet_types_data = [
                analytics_data['tweet_types']['text'],
                analytics_data['tweet_types']['photo'],
                analytics_data['tweet_types']['video'],
                analytics_data['tweet_types']['link'],
                analytics_data['tweet_types']['other']
            ]
            analytics_data['chart_tweet_types_data'] = json.dumps(chart_tweet_types_data)
            analytics_data['chart_post_types_labels'] = json.dumps(['Text', 'Photo', 'Video', 'Link', 'Other'])
            
    except Exception as e:
        error = f"Twitter API access restricted: {str(e)}"
        # Don't create sample data, return empty values
    
    return render(request, 'dashboard/twitter_analytics.html', {
        'user_data': user_data,
        'analytics_data': analytics_data,
        'error': error,
        'platform': 'twitter'
    })

@login_required
def analytics_view(request):
    """View for Facebook analytics dashboard"""
    # Reload credentials in case they were updated
    load_facebook_credentials()
    
    # Check if we have real credentials or just placeholders
    if FACEBOOK_ACCESS_TOKEN == 'YOUR_FACEBOOK_ACCESS_TOKEN':
        return redirect('config')
    
    user_data = None
    posts_data = None
    error = None
    analytics_data = {
        'total_posts': 0,
        'total_reactions': 0,
        'total_comments': 0,
        'avg_reactions_per_post': 0,
        'avg_comments_per_post': 0,
        'posts_by_month': {},
        'engagement_by_month': {},
        'top_posts': [],
        'post_types': {'text': 0, 'photo': 0, 'link': 0, 'video': 0, 'other': 0},
        'reaction_distribution': {},
        # For chart.js
        'chart_labels': [],
        'chart_posts_data': [],
        'chart_reactions_data': [],
        'chart_comments_data': [],
        'chart_post_types_labels': ['Text', 'Photo', 'Link', 'Video', 'Other'],
        'chart_post_types_data': []
    }
    
    try:
        # Get user profile
        api_url = f'https://graph.facebook.com/v19.0/me?fields=id,name,email,picture&access_token={FACEBOOK_ACCESS_TOKEN}'
        response = requests.get(api_url)
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Get user posts with reactions and comments - get more posts for analytics
            posts_url = f'https://graph.facebook.com/v19.0/me/posts?fields=id,message,created_time,reactions.summary(true),comments.summary(true),attachments{{media,type,url}}&limit=100&access_token={FACEBOOK_ACCESS_TOKEN}'
            posts_response = requests.get(posts_url)
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json().get('data', [])
                
                # Process analytics data
                if posts_data:
                    analytics_data['total_posts'] = len(posts_data)
                    total_reactions = 0
                    total_comments = 0
                    posts_by_month = {}
                    engagement_by_month = {}
                    
                    for post in posts_data:
                        # Count reactions and comments
                        reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
                        comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                        total_reactions += reactions
                        total_comments += comments
                        
                        # Determine post type
                        if 'attachments' in post and post['attachments'].get('data'):
                            attachment_type = post['attachments']['data'][0].get('type', 'other')
                            if attachment_type == 'photo':
                                analytics_data['post_types']['photo'] += 1
                            elif attachment_type == 'video':
                                analytics_data['post_types']['video'] += 1
                            elif attachment_type in ['link', 'share']:
                                analytics_data['post_types']['link'] += 1
                            else:
                                analytics_data['post_types']['other'] += 1
                        elif post.get('message'):
                            analytics_data['post_types']['text'] += 1
                        else:
                            analytics_data['post_types']['other'] += 1
                        
                        # Group by month
                        if 'created_time' in post:
                            post_date = datetime.datetime.strptime(post['created_time'][:10], '%Y-%m-%d')
                            month_key = post_date.strftime('%Y-%m')
                            month_name = post_date.strftime('%b %Y')
                            
                            if month_key not in posts_by_month:
                                posts_by_month[month_key] = {'name': month_name, 'count': 0, 'reactions': 0, 'comments': 0}
                            
                            posts_by_month[month_key]['count'] += 1
                            posts_by_month[month_key]['reactions'] += reactions
                            posts_by_month[month_key]['comments'] += comments
                    
                    # Calculate averages
                    if analytics_data['total_posts'] > 0:
                        analytics_data['total_reactions'] = total_reactions
                        analytics_data['total_comments'] = total_comments
                        analytics_data['avg_reactions_per_post'] = round(total_reactions / analytics_data['total_posts'], 1)
                        analytics_data['avg_comments_per_post'] = round(total_comments / analytics_data['total_posts'], 1)
                    
                    # Sort posts by engagement (reactions + comments)
                    sorted_posts = sorted(
                        posts_data, 
                        key=lambda x: (
                            x.get('reactions', {}).get('summary', {}).get('total_count', 0) + 
                            x.get('comments', {}).get('summary', {}).get('total_count', 0)
                        ),
                        reverse=True
                    )
                    
                    # Get top 5 posts
                    analytics_data['top_posts'] = sorted_posts[:5]
                    
                    # Process posts by month and prepare chart data
                    chart_labels = []
                    chart_posts_data = []
                    chart_reactions_data = []
                    chart_comments_data = []
                    
                    for month_key, data in sorted(posts_by_month.items()):
                        analytics_data['posts_by_month'][month_key] = data['count']
                        engagement = data['reactions'] + data['comments']
                        analytics_data['engagement_by_month'][month_key] = {
                            'name': data['name'],
                            'reactions': data['reactions'],
                            'comments': data['comments'],
                            'total': engagement
                        }
                        
                        # Add data for charts
                        chart_labels.append(data['name'])
                        chart_posts_data.append(data['count'])
                        chart_reactions_data.append(data['reactions'])
                        chart_comments_data.append(data['comments'])
                    
                    # Convert chart data to JSON for JavaScript
                    analytics_data['chart_labels'] = json.dumps(chart_labels)
                    analytics_data['chart_posts_data'] = json.dumps(chart_posts_data)
                    analytics_data['chart_reactions_data'] = json.dumps(chart_reactions_data)
                    analytics_data['chart_comments_data'] = json.dumps(chart_comments_data)
                    
                    # Add post types data for chart
                    chart_post_types_data = [
                        analytics_data['post_types']['text'],
                        analytics_data['post_types']['photo'],
                        analytics_data['post_types']['link'],
                        analytics_data['post_types']['video'],
                        analytics_data['post_types']['other']
                    ]
                    analytics_data['chart_post_types_data'] = json.dumps(chart_post_types_data)
                    analytics_data['chart_post_types_labels'] = json.dumps(['Text', 'Photo', 'Link', 'Video', 'Other'])
                    
                    # Get detailed reaction data if available
                    if len(posts_data) > 0 and 'reactions' in posts_data[0]:
                        # We would need additional API calls to get detailed reaction types
                        # This is a placeholder for that functionality
                        analytics_data['reaction_distribution'] = {
                            'LIKE': total_reactions,  # Simplified, as we don't have detailed breakdown
                        }
            else:
                error = f"Error fetching posts: {posts_response.json().get('error', {}).get('message', 'Unknown error')}"
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
    except Exception as e:
        error = str(e)
    
    return render(request, 'dashboard/analytics.html', {
        'user_data': user_data,
        'analytics_data': analytics_data,
        'error': error,
        'platform': 'facebook'
    })
