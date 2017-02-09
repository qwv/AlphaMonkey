
ALLOWED_HOSTS = []

# Database

DATABASES = {
    'default': {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'monkey',
            'USER': 'root',
            'PASSWORD': 'blackhand',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    },
    'test': {
        'ENGINE': 'mysql',
        'CONFIG': {
            'NAME': 'monkey_test',
            'USER': 'root',
            'PASSWORD': 'blackhand',
            'HOST': '127.0.0.1',
            'PORT': 3306,
        },
    }
}
