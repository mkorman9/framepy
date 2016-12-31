Feature: Controllers mapping
  Scenario: Querying controller without arguments and payload
    When GET is send to /get/sample
    Then Response status code should be equal to 200
    Then Valid response should be generated with data equal to ok

  Scenario: Querying controller with argument
    Given GET argument argument equal to something
    When GET is send to /get/echo
    Then Response status code should be equal to 200
    Then Valid response should be generated with data equal to something

  Scenario: Querying controller with payload
    Given POST payload equal to {"someVariable":"someValue","someVariable2":"someValue2"}
    When POST with payload is send to /post/echo
    Then Response status code should be equal to 200
    Then Valid response should be generated with JSON response equal to {"someVariable":"someValue","someVariable2":"someValue2"}

  Scenario: Querying controller with invalid payload
    Given POST payload equal to {"someVariable":"someValue"}
    When POST with payload is send to /post/echo
    Then Response status code should be equal to 400

  Scenario: Querying logic
    Given POST payload equal to {"value":10}
    When POST with payload is send to /post/increment
    Then Response status code should be equal to 200
    Then Valid response should be generated with JSON response equal to {"value":11}

  Scenario: Querying logic defined in configuration bean
    Given POST payload equal to {"value":10}
    When POST with payload is send to /post/decrement
    Then Response status code should be equal to 200
    Then Valid response should be generated with JSON response equal to {"value":9}
