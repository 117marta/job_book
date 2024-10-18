# Constants
LEGAL_AGE = 18
PASSWORD_STRONG = "c=%j!Qu3&#SSaz47_Of("
PASSWORD_NUMERIC = "123"
USERS_OBJECTS_PER_PAGE = 20
AVATAR_MAX_DIMENSION = 600
AVATAR_MAX_SIZE = 2 * 1024 * 1024  # 2 MB


# Forms
BIRTH_DATE_FORM_ERROR = "Please provide the correct date of birth"
PASSWORD_FORM_MATCH_ERROR = "The passwords do not match"
PASSWORD_FORM_NUMERIC_ERROR = "Password can’t be entirely numeric"
TRADE_FORM_HELP_TEXT = "You can choose several options in which you specialize"

REGISTRATION_SUCCESS_MESSAGE = "The account has been created!"
LOGIN_SUCCESS_MESSAGE = "Logged in successfully!"
LOGIN_FAIL_MESSAGE = "Incorrect email or password!"
FORM_ERROR_MESSAGE = "Errors in the form!"
LOGOUT_SUCCESS_MESSAGE = "You have been logged out!"

AVATAR_ALLOWED_CONTENT_TYPES = ("image/png", "image/jpg", "image/jpeg")
AVATAR_DIMENSION_ERROR = "Use image smaller than {max_dimension}x{max_dimension} pixels"
AVATAR_FILE_ERROR = "Invalid image file"
AVATAR_SIZE_ERROR = "Avatar size cannot be larger then 2 MB"
AVATAR_TYPE_ERROR = "Use JPEG or PNG image"


# Views
LOGIN_NECESSITY_MESSAGE = "You must be logged in to visit this page"
ADMIN_NECESSITY_MESSAGE = "You are not authorized to visit this page"
USERS_ACCEPTED = "{} user(s) have been accepted"
USERS_DELETED = "{} user(s) have been deleted"


# E-mails
EMAIL_REGISTRATION_SUBJECT = "You have just created an account on the MarBud website"
EMAIL_REGISTRATION_CONTENT = "You have successfully created an account on the MarBud website. Wait for the administration to confirm your data. After positive verification, you will be able to log in to your account."
EMAIL_ACCEPTANCE_SUBJECT = "Your account has been successfully verified"
EMAIL_ACCEPTANCE_CONTENT = "Your account has been successfully verified! From now on you can take full advantage of the service."
