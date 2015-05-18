#!/usr/bin/env ruby
# Originally created by Bryan McLellan <btm@loftninjas.org>
#     - http://blog.loftninjas.org/2012/01/12/downloading-all-the-github-repositories/
# Updated on 2015-05-17 by Sid Carter <nospam@sidcarter.com>
# Fetch the list of repositories from a Github user and 'git clone' them all
 
require 'rubygems'
require 'json'
require 'net/http'

if ARGV.length == 2
  user = ARGV[0]
  dir = ARGV[1]
else
  puts "Not enough arguments.\nUsage: get_user_repos.rb <username> <dirname>"
  exit(1)
end


if File.exists?(dir)
  puts "Target directory of '#{dir}' already exists."
  exit 1
else
  Dir.mkdir(dir)
  Dir.chdir(dir)
end

url = "https://api.github.com/users/#{user}/repos"
puts url
  
resp = Net::HTTP.get_response(URI.parse(url))
data = resp.body
 
result = JSON.parse(data)
 
result.each do |repo|
  reponame=/[a-z]+/.match(repo['name']) #don't want any "-" in the name
  puts "Fetching #{repo['html_url']} as #{reponame}"
  system "git clone #{repo['html_url']} #{reponame}"
end