package es.gul.zoe;

public class Users {

    private MessageParser parser;
    
    public Users(MessageParser parser) {
        this.parser = parser;
    }
    
    public String get(String name, String property) {
        return this.parser.get(name + "-" + property);
    }
}
