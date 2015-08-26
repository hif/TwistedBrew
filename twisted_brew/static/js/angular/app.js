
'use strict';

var twistedBrew = angular.module('twistedBrew', ['ngResource', 'ngRoute', 'yaru22.md']);

twistedBrew.config(function($routeProvider, $interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

  $routeProvider.
      when('/', {
        templateUrl: '/static/views/home.html'
      }).
      when('/messages/', {
        controller: 'MessageController',
        templateUrl: '/static/views/messages.html'
      }).
      when('/messages/:type', {
        controller: 'MessageController',
        templateUrl: '/static/views/messages.html'
      }).
      when('/menu/:restaurantId', {
        controller: 'MenuController',
        templateUrl: 'views/menu.html'
      }).
      when('/checkout', {
        controller: 'CheckoutController',
        templateUrl: 'views/checkout.html'
      }).
      when('/thank-you', {
        controller: 'ThankYouController',
        templateUrl: 'views/thank-you.html'
      }).
      when('/customer', {
        controller: 'CustomerController',
        templateUrl: 'views/customer.html'
      }).
      when('/who-we-are', {
        templateUrl: 'views/who-we-are.html'
      }).
      when('/how-it-works', {
        templateUrl: 'views/how-it-works.html'
      }).
      when('/help', {
        templateUrl: '/static/views/help.html'
      });
});

