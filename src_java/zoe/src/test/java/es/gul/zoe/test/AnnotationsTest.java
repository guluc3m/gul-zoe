package es.gul.zoe.test;

import java.util.List;

import org.junit.Test;

import es.gul.zoe.AnnotatedAgentLoader;
import es.gul.zoe.MessageParser;
import es.gul.zoe.annotations.Agent;
import es.gul.zoe.annotations.Message;
import es.gul.zoe.annotations.Param;
import static org.junit.Assert.*;

public class AnnotationsTest {

    @Agent("test")
	public static class MyAgent {
		
		public boolean somethingCalled = false;
		public boolean noTagsNoParamsCalled = false;
		public boolean tagNoParamsCalled = false;
		public boolean twoTagsNoParamsCalled = false;
		public boolean tagAndParamsCalled = false;
		public String a = null;
		public String b = null;
		public List<String> c = null;
		public MessageParser parser = null;
		
		@Message
		public void noTagsNoParams() {
			somethingCalled = true;
			noTagsNoParamsCalled = true;
		}
		
		@Message(tags = "tag")
		public void tagNoParams() {
			somethingCalled = true;
			tagNoParamsCalled = true;
		}

		@Message(tags = {"tag1", "tag2"})
		public void twoTagNoParams() {
			somethingCalled = true;
			twoTagsNoParamsCalled = true;
		}

		@Message(tags = "tag3")
		public void tagAndParams(@Param("a") String a, 
				                 @Param("b") String b, 
				                 @Param("c") List<String> c, 
				                             MessageParser parser) {
			somethingCalled = true;
			tagAndParamsCalled = true;
			this.a = a;
			this.b = b;
			this.c = c;
			this.parser = parser;
		}
	}
	
	@Test
	public void testNoTagsNoParams() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b";
		launcher.receive(new MessageParser(msg));
		assertTrue(agent.noTagsNoParamsCalled);
	}

	@Test
	public void testTagNoParams() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b&tag=tag";
		launcher.receive(new MessageParser(msg));
		assertTrue(agent.tagNoParamsCalled);
	}

	@Test
	public void testTwoTagNoParams() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b&tag=tag1&tag=tag2";
		launcher.receive(new MessageParser(msg));
		assertTrue(agent.twoTagsNoParamsCalled);
	}

	@Test
	public void testTagCombinations1() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b&tag=tag&tag=tag2";
		launcher.receive(new MessageParser(msg));
		assertTrue(agent.tagNoParamsCalled);
	}

	@Test
	public void testTagCombinations2() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b&tag=tag&tag=tag1&tag=tag2";
		launcher.receive(new MessageParser(msg));
		assertFalse(agent.somethingCalled);
	}
	
	@Test
	public void testTagAndParams1() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b&tag=tag3";
		launcher.receive(new MessageParser(msg));
		assertTrue(agent.tagAndParamsCalled);
		assertEquals("a", agent.a);
		assertEquals("b", agent.b);
	}

	@Test
	public void testTagAndParams2() throws Exception {
		MyAgent agent = new MyAgent();
		AnnotatedAgentLoader launcher = new AnnotatedAgentLoader(agent);
		String msg = "a=a&b=b&c=c1&c=c2&tag=tag3";
		MessageParser parser = new MessageParser(msg);
		launcher.receive(parser);
		assertTrue(agent.tagAndParamsCalled);
		assertEquals("a", agent.a);
		assertEquals("b", agent.b);
		assertNotNull(agent.c);
		assertEquals(2, agent.c.size());
		assertEquals("c1", agent.c.get(0));
		assertEquals("c2", agent.c.get(1));
		assertNotNull(agent.parser);
		assertEquals(parser, agent.parser);
	}
}
