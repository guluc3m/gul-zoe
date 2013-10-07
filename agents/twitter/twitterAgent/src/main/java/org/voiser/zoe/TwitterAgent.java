/*
 * This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
 *
 * Copyright (c) 2013 David Muñoz Díaz <david@gul.es>
 *
 * This file is distributed under the MIT LICENSE
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
package org.voiser.zoe;

import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;
import es.gul.zoe.MessageParser;
import es.gul.zoe.Users;
import es.gul.zoe.annotations.Agent;
import es.gul.zoe.annotations.Message;
import es.gul.zoe.annotations.Param;

/**
 * Sends messages to Twitter.
 * @author david
 *
 */
@Agent("twitter")
public class TwitterAgent {

    private Users users;
    private Twitter twitter;
    
    /**
     * 
     */
    public TwitterAgent() {
        String consumerKey = System.getenv("zoe_twitter_consumer_key");
        String consumerSecret = System.getenv("zoe_twitter_consumer_secret");
        String accessToken = System.getenv("zoe_twitter_access_token");
        String accessTokenSecret = System.getenv("zoe_twitter_access_token_secret");
                
        ConfigurationBuilder cb = new ConfigurationBuilder();
        cb.setDebugEnabled(true)
            .setOAuthConsumerKey(consumerKey)
            .setOAuthConsumerSecret(consumerSecret)
            .setOAuthAccessToken(accessToken)
            .setOAuthAccessTokenSecret(accessTokenSecret);
        
        TwitterFactory tf = new TwitterFactory(cb.build());
        twitter = tf.getInstance();        
    }
    
    /**
     * Users notification
     * @param parser
     */
    @Message(tags = {"users", "notification"})
    public void updateUsers(MessageParser parser) {
        System.out.println("Receiving users notification");
        Users users = new Users(parser);
        this.users = users;
    }
    
    /**
     * Post message to Twitter
     * @param to
     * @param message
     */
    @Message
    public void send(@Param("to")  String to, 
                     @Param("msg") String message) {
        
        // Ensure we have users notification
        if (this.users == null) {
            System.out.println("I don't have users information.");
            return;
        }
        
        // Try to find a user with the given name and a twitter account.
        // If no one is found, assume that the destination is a twitter user, not a zone one.
        String dest = this.users.get(to, "twitter");
        if (dest == null) {
            System.out.println("Can't find a user called " + to + ". I'll assume it is a twitter account");
            dest = to;
        }
        
        // Send the message to Twitter
        try {
            String finalMsg = to == null ? message : "@" + dest + " " + message;
            String ts = " (" + System.currentTimeMillis() + ")";
            twitter.updateStatus(finalMsg + ts);
            System.out.println("twitted: " + finalMsg);
        } catch (TwitterException e) {
            e.printStackTrace();
        }
    }
}
