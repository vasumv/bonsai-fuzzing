package chocopy.fuzz;

import chocopy.common.astnodes.Program;
import chocopy.reference.RefAnalysis;
import chocopy.reference.RefCodeGen;
import chocopy.reference.RefParser;
import com.pholser.junit.quickcheck.From;
import edu.berkeley.cs.jqf.fuzz.Fuzz;
import edu.berkeley.cs.jqf.fuzz.JQF;
import org.junit.runner.RunWith;

import static org.junit.Assume.assumeFalse;

@RunWith(JQF.class)
public class AnalysisTargetRaw {

    /** Entry point for running reference semantic analysis with Chocopy code generator */
    @Fuzz
    public void runParserRaw(@From(ArbitraryLengthStringGenerator.class) String code) {
        Program program = RefParser.process(code, false);
        assumeFalse(program.hasErrors());
    }

    /** Entry point for running reference semantic analysis with Chocopy code generator */
    @Fuzz
    public void runAnalysisRaw(@From(ArbitraryLengthStringGenerator.class) String code) {
        Program program = RefParser.process(code, false);
        assumeFalse(program.hasErrors());
        RefAnalysis.process(program);
        assumeFalse(program.hasErrors());
    }

    /** Entry point for running reference semantic analysis with Chocopy code generator */
    @Fuzz
    public void runCodeGenRaw(@From(ArbitraryLengthStringGenerator.class) String code) {
        Program program = RefParser.process(code, false);
        assumeFalse(program.hasErrors());
        program = RefAnalysis.process(program);
        assumeFalse(program.hasErrors());
        RefCodeGen.process(program);
    }
}
