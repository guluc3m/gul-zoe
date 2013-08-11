package org.voiser.zoe;

import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;
import es.gul.zoe.annotations.Agent;
import es.gul.zoe.annotations.Message;
import es.gul.zoe.annotations.Param;

@Agent("twitter")
public class TwitterAgent {

    @Message
    public void send(@Param("to") String to, 
                     @Param("msg") String message) {
        
        String finalMsg = to == null ? message : "@" + to + " " + message;
        
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
        Twitter twitter = tf.getInstance();
        
        try {
            twitter.updateStatus(finalMsg);
            System.out.println("twitted: " + finalMsg);
        } catch (TwitterException e) {
            e.printStackTrace();
        }
    }
}
