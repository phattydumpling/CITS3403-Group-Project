from app import create_app, db
from app.models import User, StudySession, Task, WellnessCheck, MoodEntry, Friendship, FriendRequest
from flask import session

def remove_all_users():
    app = create_app()
    with app.app_context():
        try:
            # First, delete all related records
            print("Deleting related records...")
            
            # Delete all mood entries
            MoodEntry.query.delete()
            print("Deleted mood entries")
            
            # Delete all wellness checks
            WellnessCheck.query.delete()
            print("Deleted wellness checks")
            
            # Delete all tasks
            Task.query.delete()
            print("Deleted tasks")
            
            # Delete all study sessions
            StudySession.query.delete()
            print("Deleted study sessions")
            
            # Delete all friend requests
            FriendRequest.query.delete()
            print("Deleted friend requests")
            
            # Delete all friendships
            Friendship.query.delete()
            print("Deleted friendships")
            
            # Finally, delete all users
            User.query.delete()
            print("Deleted all users")
            
            # Commit the changes
            db.session.commit()
            print("Successfully removed all users and related data!")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    remove_all_users() 