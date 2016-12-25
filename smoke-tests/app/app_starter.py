import framepy

if __name__ == '__main__':
    framepy.scan_packages()
    framepy.core.init_context(properties_file='properties.ini')

    framepy.core.start_standalone_application()
