package es.gul.zoe;

import java.lang.annotation.Annotation;
import java.lang.reflect.Method;
import java.util.LinkedList;
import java.util.List;

import es.gul.zoe.annotations.Message;
import es.gul.zoe.annotations.Param;

public class AnnotatedAgentLoader implements Agent {

    private Listener listener;
	private Object agent;
	private es.gul.zoe.annotations.Agent annotation;
	private List<Method> methods;
	
	public AnnotatedAgentLoader(Object agent) {
		this.agent = agent;
		this.methods = new LinkedList<>();
		
		es.gul.zoe.annotations.Agent ann = agent.getClass().getAnnotation(es.gul.zoe.annotations.Agent.class);
		if (ann == null) {
		    throw new RuntimeException("Agent " + agent + " is not an annotated agent");
		}
		this.annotation = ann;

		Method[] methods = agent.getClass().getDeclaredMethods();
		for (Method m : methods) {
			if (m.isAnnotationPresent(Message.class)) {
				this.methods.add(m);
			}
		}
	}
	
	public void start() {
        this.listener = new Listener(annotation.value(), this);
	    listener.start();
	}
	
	@Override
	public void receive(MessageParser parser) throws Exception {
		Method theMethod = chooseMethod(parser);
		if (theMethod == null) {
			return;
		}
		Object[] params = chooseParams(parser, theMethod);
		Object returned = theMethod.invoke(this.agent, params);
		if (returned != null) {
		    String msg = returned.toString();
		    System.out.println("Sending back to Zoe " + msg);
		    listener.sendbus(msg);
		}
	}
	
	private Method chooseMethod(MessageParser parser) {
		List<String> tags = parser.tags();
		List<Method> chosenMethods = new LinkedList<>();
		for (Method m : methods) {
			if (match(m, tags)) {
				chosenMethods.add(m);
			}
		}
		if (chosenMethods.size() == 0) {
			System.out.println("No method will be called");
			return null;
		} else if (chosenMethods.size() > 1) {
			System.out.println("More than 1 candidate:");
			System.out.println("  Message: " + parser);
			for (Method m : chosenMethods) {
				System.out.println("  Candidate: " + m);
			}
			return null;
		}
		Method theMethod = chosenMethods.get(0);
		System.out.println("The chosen method is " + theMethod);
		return theMethod;
	}
	
	private Object[] chooseParams(MessageParser parser, Method method) {
		int nParams = method.getParameterTypes().length;
		Class<?>[] paramTypes = method.getParameterTypes();
		Object[] paramValues = new Object[nParams];
		Annotation[][] annotations = method.getParameterAnnotations(); 
		for (int i = 0; i < nParams; i++) {
			Class<?> paramType = paramTypes[i];
			Annotation[] paramAnnotation = annotations[i];
			if (paramAnnotation.length == 0) {
				paramValues[i] = null;
			}
			Param theAnnotation = null;
			for (Annotation a : paramAnnotation) {
				if (a instanceof Param) {
					theAnnotation = (Param)a;
				}
			}
			if (theAnnotation != null) {
				String messageParamName = theAnnotation.value();
				Object messageParamValue = null;
				if (paramType == String.class) {
					messageParamValue = parser.get(messageParamName);
				} else if (paramType == List.class){
					messageParamValue = parser.list(messageParamName);
				}
				paramValues[i] = messageParamValue;
			}
			if (paramTypes[i] == MessageParser.class) {
				paramValues[i] = parser;
			}
		}
		return paramValues;
	}
	
	private boolean match(Method m, List<String> tags) {
		Message annotation = m.getAnnotation(Message.class);
		String[] requiredTags = annotation.tags();
		if (tags == null) {
			if (requiredTags == null 
					|| requiredTags.length == 0 
					|| (requiredTags.length == 1 && requiredTags[0].equals(""))) {
				return true;
			} else {
				return false;
			}
		}
		boolean matches = true;
		for (String requiredTag : requiredTags) {
			if (!tags.contains(requiredTag)) {
				matches = false;
			}
		}
		return matches;
	}
	
	private static class AgentLauncher implements Runnable {

        private Object agent;
        
        public AgentLauncher(Object agent) {
            this.agent = agent;
        }

        @Override
        public void run() {
            new AnnotatedAgentLoader(agent).start();
        }
    }
	
	public static void main(String... args) {
        for (String agentClass : args) {
            try {
                final Class<?> k = Class.forName(agentClass);
                Object agent = k.newInstance();
                System.out.println("Starting agent " + agent);
                AgentLauncher launcher = new AgentLauncher(agent);
                new Thread(launcher).start();
            } catch (ClassNotFoundException | IllegalAccessException | InstantiationException e) {
                System.err.println("Can't find agent class " + agentClass);
            }
        }
    }
}
