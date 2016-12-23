Feature: Controllers mapping
  Scenario: Querying controller without arguments and payload
    When GET is send to /data/sample
    Then Valid response should be generated with data equals to ok

  Scenario: Querying controller with argument
    Given GET argument argument equal to something
    When GET is send to /data/echo
    Then Valid response should be generated with data equals to something
